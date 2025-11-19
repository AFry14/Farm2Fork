from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    
    class Meta:
        app_label = 'market'
        ordering = ['-is_featured', 'name']
    
    def __str__(self):
        return self.name

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

# users table - this will house user info with user_type (vendor/consumer)

# ordes table - this will contain order records (user & vendor IDs required)

