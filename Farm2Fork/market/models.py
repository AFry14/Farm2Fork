from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal

# Vendor Application Model - stores applications before approval
class VendorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_applications')
    business_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    description = models.TextField()
    story_mission = models.TextField()
    ships_goods = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} - {self.get_status_display()}"

# vendors table - this houses required info for vendors (a vendor record) - once users table is defined, much of this can be removed
class Vendor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    story_mission = models.TextField(blank=True, null=True, help_text="Vendor's story and mission")
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    service_area = models.TextField(blank=True, null=True, help_text="Geographic areas where vendor provides service")
    ships_goods = models.BooleanField(default=False, help_text="Whether vendor ships products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    feature_priority = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_vendors')
    application = models.OneToOneField('VendorApplication', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_vendor')

    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    @property
    def price_range(self):
        """Get price range of vendor's products"""
        products = self.products.all()
        if products.exists():
            prices = [product.price for product in products]
            min_price = min(prices)
            max_price = max(prices)
            if min_price == max_price:
                return f"${min_price}"
            return f"${min_price} - ${max_price}"
        return "No products"
    
    def has_products_below_price(self, min_price):
        """Check if vendor has products below the specified minimum price"""
        return self.products.filter(price__lt=float(min_price)).exists()
    
    def has_products_above_price(self, max_price):
        """Check if vendor has products above the specified maximum price"""
        return self.products.filter(price__gt=float(max_price)).exists()

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat'),
        ('grains', 'Grains'),
        ('herbs', 'Herbs'),
        ('prepared', 'Prepared Foods'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    is_featured = models.BooleanField(default=False, help_text="Featured products appear at top of vendor page")
    max_quantity = models.IntegerField(default=100, help_text="Maximum quantity that can be ordered per customer")
    track_inventory = models.BooleanField(default=False, help_text="Enable inventory tracking for this product")
    stock_quantity = models.IntegerField(null=True, blank=True, help_text="Current stock quantity (required if inventory tracking enabled)")
    is_available = models.BooleanField(default=True, help_text="Product availability status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    
    class Meta:
        app_label = 'market'
        ordering = ['-is_featured', 'name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate that stock_quantity is provided when track_inventory is True"""
        if self.track_inventory and (self.stock_quantity is None or self.stock_quantity < 0):
            raise ValidationError({
                'stock_quantity': 'Stock quantity is required and must be non-negative when inventory tracking is enabled.'
            })
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='reviews')
    consumer_name = models.CharField(max_length=100, help_text="Name of the reviewer")
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.consumer_name} - {self.rating} stars for {self.vendor.name}"
    
    @property
    def has_response(self):
        """Check if this review has a vendor response"""
        return hasattr(self, 'response')

# Vendor Team Member Model - links users to vendors
class VendorTeamMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_teams')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='team_members')
    is_owner = models.BooleanField(default=False, help_text="True for the user who created the vendor")
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_team_members')
    
    class Meta:
        app_label = 'market'
        unique_together = ['user', 'vendor']
        ordering = ['-is_owner', 'joined_at']
    
    def __str__(self):
        role = "Owner" if self.is_owner else "Member"
        return f"{self.user.username} - {role} of {self.vendor.name}"

# Product Media Model - stores product images
class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media_items')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False, help_text="Main product image")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0, help_text="Order for sorting images")
    
    class Meta:
        app_label = 'market'
        ordering = ['is_primary', 'order', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"

# Review Response Model - vendor responses to reviews
class ReviewResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='review_responses')
    response_text = models.TextField(max_length=1000, help_text="Response text (max 1000 characters)")
    is_public = models.BooleanField(default=True, help_text="Public vs private response")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['-created_at']
    
    def __str__(self):
        visibility = "Public" if self.is_public else "Private"
        return f"{visibility} response to review by {self.review.consumer_name}"

# Message Model - in-app messaging system
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    subject = models.CharField(max_length=200)
    body = models.TextField(max_length=1000, help_text="Message body (max 1000 characters)")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}: {self.subject}"

# Create your models here.

# consumers table - this will house required info for consumer users (a consumer record) - once users table is defined, much of this can be removed
class Consumer(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    """Shopping cart for a user and vendor pair"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'market'
        unique_together = ['user', 'vendor']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.user.username} - {self.vendor.name}"
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Individual item in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'market'
        unique_together = ['cart', 'product']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} in {self.cart}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return Decimal(self.quantity) * self.product.price

class Order(models.Model):
    """Order model for completed purchases"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping/Delivery information
    shipping_address = models.TextField(blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_state = models.CharField(max_length=100, blank=True, null=True)
    shipping_zip_code = models.CharField(max_length=10, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)
    
    # Buyer location for analytics
    buyer_city = models.CharField(max_length=100, blank=True, null=True)
    buyer_state = models.CharField(max_length=100, blank=True, null=True)
    buyer_zip_code = models.CharField(max_length=10, blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True, help_text="Order notes or special instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.vendor.name} - ${self.total_price}"
    
    @property
    def is_completed(self):
        """Check if order is in a completed state"""
        return self.status in ['completed', 'delivered']
    
    @property
    def item_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    """Individual item in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    product_name = models.CharField(max_length=100, help_text="Snapshot of product name at time of order")
    product_category = models.CharField(max_length=20, help_text="Snapshot of product category at time of order")
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, help_text="Price per unit at time of order")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'market'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order #{self.order.id}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        if not self.subtotal:
            self.subtotal = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)

