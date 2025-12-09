from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Min, Max, Count, Sum, Avg, F, DecimalField
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from .models import Product, Vendor, Consumer, Review, Cart, CartItem, Order, OrderItem, VendorApplication, VendorTeamMember, ProductMedia, ReviewResponse, Message
from .forms import VendorApplicationForm, VendorEditForm, ProductForm, ReviewResponseForm, UserProfileForm, PasswordChangeFormCustom
from .decorators import vendor_team_required, vendor_owner_required
from .utils import send_private_review_response_notification, send_new_message_notification

def market_home(request):
    """Main market page with vendor listings and search/filter functionality"""
    vendors = Vendor.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    location_filter = request.GET.get('location', '')
    category_filter = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    if search_query:
        vendors = vendors.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if location_filter:
        vendors = vendors.filter(
            Q(city__icontains=location_filter) | 
            Q(state__icontains=location_filter) |
            Q(service_area__icontains=location_filter)
        )
    
    # Filter by product category if specified
    if category_filter:
        vendors_with_category = vendors.filter(products__category=category_filter).distinct()
        vendors = vendors_with_category
    
    # Filter by price range if specified - include vendors who have ANY products in range
    if min_price or max_price:
        filtered_vendors = []
        for vendor in vendors:
            vendor_products = vendor.products.all()
            if vendor_products.exists():
                # Check if vendor has ANY products within the price range
                has_products_in_range = False
                
                if min_price and max_price:
                    # Both min and max specified
                    has_products_in_range = vendor_products.filter(
                        price__gte=float(min_price),
                        price__lte=float(max_price)
                    ).exists()
                elif min_price:
                    # Only min price specified
                    has_products_in_range = vendor_products.filter(
                        price__gte=float(min_price)
                    ).exists()
                elif max_price:
                    # Only max price specified
                    has_products_in_range = vendor_products.filter(
                        price__lte=float(max_price)
                    ).exists()
                
                if has_products_in_range:
                    filtered_vendors.append(vendor)
        vendors = filtered_vendors
    
    # Get all available categories for filter dropdown
    all_categories = Product.CATEGORY_CHOICES
    
    # Get price range for filter
    all_products = Product.objects.all()
    if all_products.exists():
        price_range = {
            'min': all_products.aggregate(Min('price'))['price__min'],
            'max': all_products.aggregate(Max('price'))['price__max']
        }
    else:
        price_range = {'min': 0, 'max': 0}
    
    # Add price warning information to each vendor
    vendors_with_warnings = []
    for vendor in vendors:
        vendor_dict = {
            'vendor': vendor,
            'has_products_below_min': False,
            'has_products_above_max': False,
        }
        
        if min_price:
            vendor_dict['has_products_below_min'] = vendor.has_products_below_price(min_price)
        if max_price:
            vendor_dict['has_products_above_max'] = vendor.has_products_above_price(max_price)
            
        vendors_with_warnings.append(vendor_dict)
    
    context = {
        'vendors_with_warnings': vendors_with_warnings,
        'search_query': search_query,
        'location_filter': location_filter,
        'category_filter': category_filter,
        'min_price': min_price,
        'max_price': max_price,
        'categories': all_categories,
        'price_range': price_range,
    }
    
    return render(request, 'market/market_home.html', context)

def vendor_detail(request, vendor_id):
    """Individual vendor home page with products tab"""
    vendor = get_object_or_404(Vendor, id=vendor_id, is_active=True)
    
    # Get all products for this vendor, ordered by featured first, then by category
    all_products = vendor.products.all()
    featured_products = all_products.filter(is_featured=True)
    
    # Group products by category
    products_by_category = {}
    for product in all_products:
        category = product.get_category_display()
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    
    # Get reviews for this vendor
    reviews = vendor.reviews.all()[:5]  # Show latest 5 reviews
    
    # Get cart information if user is authenticated
    cart_item_count = 0
    if request.user.is_authenticated:
        cart_item_count = get_cart_item_count(request.user, vendor)
    
    context = {
        'vendor': vendor,
        'featured_products': featured_products,
        'products_by_category': products_by_category,
        'reviews': reviews,
        'cart_item_count': cart_item_count,
    }
    
    return render(request, 'market/vendor_detail.html', context)

def product_list(request):
    products = Product.objects.all() #type: ignore
    return render(request, 'market/product_list.html', {'products': products})

def vendor_list(request):
    vendors = Vendor.objects.all() #type: ignore
    return render(request, 'market/vendor_list.html', {'vendors': vendors})

def consumer_list(request):
    consumers = Consumer.objects.all() #type: ignore
    return render(request, 'market/consumer_list.html', {'consumers': consumers})

# Cart helper functions
def get_or_create_cart(user, vendor):
    """Get or create a cart for a user and vendor"""
    cart, created = Cart.objects.get_or_create(user=user, vendor=vendor)
    return cart

def get_cart_item_count(user, vendor):
    """Get the total item count for a user's cart with a specific vendor"""
    try:
        cart = Cart.objects.get(user=user, vendor=vendor)
        return cart.item_count
    except Cart.DoesNotExist:
        return 0

# Cart views
@login_required
def cart_detail(request, vendor_id):
    """View cart for a specific vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    cart = get_or_create_cart(request.user, vendor)
    
    context = {
        'cart': cart,
        'vendor': vendor,
        'items': cart.items.all(),
    }
    
    return render(request, 'market/cart_detail.html', context)

@login_required
def my_carts(request):
    """View all carts for the logged-in user"""
    carts = Cart.objects.filter(user=request.user).select_related('vendor').prefetch_related('items')
    
    context = {
        'carts': carts,
    }
    
    return render(request, 'market/my_carts.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('vendor_detail', vendor_id=product.vendor.id)
        
        if quantity > product.max_quantity:
            messages.error(request, f'Maximum quantity allowed is {product.max_quantity}.')
            return redirect('vendor_detail', vendor_id=product.vendor.id)
        
        # Get or create cart for this vendor
        cart = get_or_create_cart(request.user, product.vendor)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.max_quantity:
                messages.error(request, f'Adding {quantity} would exceed the maximum quantity of {product.max_quantity}.')
                return redirect('vendor_detail', vendor_id=product.vendor.id)
            cart_item.quantity = new_quantity
            cart_item.save()
        
        messages.success(request, f'Added {quantity} {product.name} to your cart.')
        return redirect('vendor_detail', vendor_id=product.vendor.id)
    
    return redirect('market_home')

@login_required
def update_cart_item(request, item_id):
    """Update the quantity of a cart item"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('cart_detail', vendor_id=cart_item.cart.vendor.id)
        
        if quantity > cart_item.product.max_quantity:
            messages.error(request, f'Maximum quantity allowed is {cart_item.product.max_quantity}.')
            return redirect('cart_detail', vendor_id=cart_item.cart.vendor.id)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, f'Updated {cart_item.product.name} quantity to {quantity}.')
        return redirect('cart_detail', vendor_id=cart_item.cart.vendor.id)
    
    return redirect('market_home')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        vendor_id = cart_item.cart.vendor.id
        cart_item.delete()
        
        messages.success(request, f'Removed {product_name} from your cart.')
        return redirect('cart_detail', vendor_id=vendor_id)
    
    return redirect('market_home')

@login_required
def clear_cart(request, vendor_id):
    """Clear all items from a cart and delete the cart"""
    if request.method == 'POST':
        vendor = get_object_or_404(Vendor, id=vendor_id)
        try:
            cart = Cart.objects.get(user=request.user, vendor=vendor)
            cart.delete()
            messages.success(request, f'Cart for {vendor.name} has been cleared.')
        except Cart.DoesNotExist:
            messages.info(request, 'Cart is already empty.')
        
        return redirect('vendor_detail', vendor_id=vendor_id)
    
    return redirect('market_home')

@login_required
def cart_count(request, vendor_id):
    """Get cart item count for a vendor (AJAX endpoint)"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    count = get_cart_item_count(request.user, vendor)
    return JsonResponse({'count': count})

# Vendor Application Views
def apply_to_be_vendor(request):
    """Public page for users to apply to become a vendor"""
    # If user is not authenticated, redirect to login with next parameter
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to apply to become a vendor.')
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    
    # Check if user already has pending applications
    pending_applications = VendorApplication.objects.filter(
        applicant=request.user,
        status='pending'
    )
    
    if request.method == 'POST':
        form = VendorApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.status = 'pending'
            application.save()
            messages.success(
                request, 
                'Your vendor application has been submitted successfully! '
                'You will be notified once it has been reviewed by an administrator.'
            )
            return redirect('apply_to_be_vendor')
    else:
        form = VendorApplicationForm(user=request.user)
        # Pre-fill email if available
        if request.user.email:
            form.fields['email'].initial = request.user.email
    
    context = {
        'form': form,
        'pending_applications': pending_applications,
    }
    
    return render(request, 'market/vendor_application.html', context)

# Vendor Team Management Views
@vendor_team_required()
def vendor_team_list(request, vendor_id):
    """View all team members for a vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    team_members = VendorTeamMember.objects.filter(vendor=vendor).select_related('user', 'added_by')
    
    # Check if current user is owner
    is_owner = VendorTeamMember.objects.filter(
        user=request.user,
        vendor=vendor,
        is_owner=True
    ).exists() or request.user.is_staff
    
    context = {
        'vendor': vendor,
        'team_members': team_members,
        'is_owner': is_owner,
    }
    
    return render(request, 'market/vendor_team_list.html', context)

@vendor_team_required()
def add_team_member(request, vendor_id):
    """Add a user to the vendor team"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    # Check if user is a team member (required by decorator, but double-check)
    is_team_member = VendorTeamMember.objects.filter(
        user=request.user,
        vendor=vendor
    ).exists() or request.user.is_staff
    
    if not is_team_member:
        messages.error(request, 'You do not have permission to add team members.')
        return redirect('vendor_team_list', vendor_id=vendor_id)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        if not username:
            messages.error(request, 'Please provide a username.')
            return redirect('add_team_member', vendor_id=vendor_id)
        
        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f'User "{username}" does not exist.')
            return redirect('add_team_member', vendor_id=vendor_id)
        
        # Check if user is already on the team
        if VendorTeamMember.objects.filter(user=user_to_add, vendor=vendor).exists():
            messages.warning(request, f'User "{username}" is already a member of this vendor team.')
            return redirect('vendor_team_list', vendor_id=vendor_id)
        
        # Add user to team
        VendorTeamMember.objects.create(
            user=user_to_add,
            vendor=vendor,
            is_owner=False,
            added_by=request.user
        )
        
        messages.success(request, f'Successfully added {username} to the vendor team.')
        return redirect('vendor_team_list', vendor_id=vendor_id)
    
    context = {
        'vendor': vendor,
    }
    
    return render(request, 'market/add_team_member.html', context)

@vendor_owner_required()
def remove_team_member(request, vendor_id, user_id):
    """Remove a user from the vendor team (owner only)"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Prevent removing the owner
    team_member = VendorTeamMember.objects.filter(
        user=user_to_remove,
        vendor=vendor
    ).first()
    
    if not team_member:
        messages.error(request, 'User is not a member of this vendor team.')
        return redirect('vendor_team_list', vendor_id=vendor_id)
    
    if team_member.is_owner:
        messages.error(request, 'Cannot remove the vendor owner. Transfer ownership first.')
        return redirect('vendor_team_list', vendor_id=vendor_id)
    
    if request.method == 'POST':
        username = user_to_remove.username
        team_member.delete()
        messages.success(request, f'Successfully removed {username} from the vendor team.')
        return redirect('vendor_team_list', vendor_id=vendor_id)
    
    context = {
        'vendor': vendor,
        'user_to_remove': user_to_remove,
    }
    
    return render(request, 'market/remove_team_member.html', context)

# Vendor Profile Management
@vendor_team_required()
def edit_vendor_profile(request, vendor_id):
    """Edit vendor profile - accessible to all team members"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        form = VendorEditForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor profile updated successfully!')
            return redirect('vendor_detail', vendor_id=vendor.id)
    else:
        form = VendorEditForm(instance=vendor)
    
    context = {
        'vendor': vendor,
        'form': form,
    }
    
    return render(request, 'market/vendor_edit.html', context)

# Product Management Views
@vendor_team_required()
def vendor_products_list(request, vendor_id):
    """List all products for a vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    products = Product.objects.filter(vendor=vendor).select_related('vendor').prefetch_related('media_items')
    
    # Filter by category if provided
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category=category_filter)
    
    # Search by name if provided
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    context = {
        'vendor': vendor,
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    
    return render(request, 'market/vendor_products_list.html', context)

@vendor_team_required()
def create_product(request, vendor_id):
    """Create a new product"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, vendor=vendor)
        if form.is_valid():
            product = form.save(commit=True)
            
            # Handle image uploads
            images = request.FILES.getlist('images')
            if images:
                for idx, image in enumerate(images):
                    ProductMedia.objects.create(
                        product=product,
                        image=image,
                        is_primary=(idx == 0),  # First image is primary
                        order=idx
                    )
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('vendor_products_list', vendor_id=vendor.id)
    else:
        form = ProductForm(vendor=vendor)
    
    context = {
        'vendor': vendor,
        'form': form,
    }
    
    return render(request, 'market/product_create.html', context)

@vendor_team_required()
def edit_product(request, vendor_id, product_id):
    """Edit an existing product"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, vendor=vendor)
        if form.is_valid():
            product = form.save(commit=True)
            
            # Handle new image uploads
            images = request.FILES.getlist('images')
            if images:
                # Get current max order
                from django.db.models import Max
                max_order = product.media_items.aggregate(Max('order'))['order__max'] or -1
                for idx, image in enumerate(images):
                    ProductMedia.objects.create(
                        product=product,
                        image=image,
                        is_primary=False,  # Don't auto-set as primary when adding to existing
                        order=max_order + idx + 1
                    )
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('vendor_products_list', vendor_id=vendor.id)
    else:
        form = ProductForm(instance=product, vendor=vendor)
    
    # Get existing media
    existing_media = product.media_items.all()
    
    context = {
        'vendor': vendor,
        'product': product,
        'form': form,
        'existing_media': existing_media,
    }
    
    return render(request, 'market/product_edit.html', context)

@vendor_team_required()
def delete_product(request, vendor_id, product_id):
    """Delete a product"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    # Check if product is in any active carts
    cart_items = CartItem.objects.filter(product=product)
    in_carts = cart_items.exists()
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('vendor_products_list', vendor_id=vendor.id)
    
    context = {
        'vendor': vendor,
        'product': product,
        'in_carts': in_carts,
        'cart_count': cart_items.count() if in_carts else 0,
    }
    
    return render(request, 'market/product_delete.html', context)

@vendor_team_required()
def bulk_product_operations(request, vendor_id):
    """Bulk operations on products"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    products = Product.objects.filter(vendor=vendor)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_products = request.POST.getlist('selected_products')
        
        if not selected_products:
            messages.error(request, 'Please select at least one product.')
            return redirect('bulk_product_operations', vendor_id=vendor_id)
        
        selected_products_qs = products.filter(id__in=selected_products)
        count = selected_products_qs.count()
        
        if action == 'price_set':
            try:
                price = float(request.POST.get('price_value', 0))
                if price <= 0:
                    raise ValueError
                selected_products_qs.update(price=price)
                messages.success(request, f'Updated price to ${price:.2f} for {count} product(s).')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid price value.')
        
        elif action == 'price_increase':
            try:
                amount = float(request.POST.get('price_value', 0))
                if amount < 0:
                    raise ValueError
                for product in selected_products_qs:
                    product.price += amount
                    product.save()
                messages.success(request, f'Increased price by ${amount:.2f} for {count} product(s).')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid price value.')
        
        elif action == 'price_decrease':
            try:
                amount = float(request.POST.get('price_value', 0))
                if amount < 0:
                    raise ValueError
                for product in selected_products_qs:
                    product.price = max(0, product.price - amount)
                    product.save()
                messages.success(request, f'Decreased price by ${amount:.2f} for {count} product(s).')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid price value.')
        
        elif action == 'price_multiply':
            try:
                multiplier = float(request.POST.get('price_value', 1))
                if multiplier <= 0:
                    raise ValueError
                for product in selected_products_qs:
                    product.price *= multiplier
                    product.save()
                messages.success(request, f'Multiplied price by {multiplier:.2f} for {count} product(s).')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid multiplier value.')
        
        elif action == 'toggle_availability':
            # Toggle availability (set all to True or False based on first product)
            first_product = selected_products_qs.first()
            new_value = not first_product.is_available if first_product else True
            selected_products_qs.update(is_available=new_value)
            status = 'available' if new_value else 'unavailable'
            messages.success(request, f'Set {count} product(s) to {status}.')
        
        elif action == 'set_category':
            category = request.POST.get('category_value')
            if category:
                selected_products_qs.update(category=category)
                category_name = dict(Product.CATEGORY_CHOICES).get(category, category)
                messages.success(request, f'Set category to {category_name} for {count} product(s).')
            else:
                messages.error(request, 'Please select a category.')
        
        elif action == 'delete':
            product_names = list(selected_products_qs.values_list('name', flat=True))
            selected_products_qs.delete()
            messages.success(request, f'Deleted {count} product(s): {", ".join(product_names[:5])}{"..." if count > 5 else ""}')
        
        return redirect('vendor_products_list', vendor_id=vendor_id)
    
    # GET request - show form
    context = {
        'vendor': vendor,
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
    }
    
    return render(request, 'market/bulk_product_operations.html', context)

# Review Management Views
@vendor_team_required()
def vendor_reviews(request, vendor_id):
    """View all reviews for a vendor"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    all_reviews = Review.objects.filter(vendor=vendor).select_related('vendor').prefetch_related('response')
    
    # Filter by rating if provided
    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        all_reviews = all_reviews.filter(rating=rating_filter)
    
    # Sort options
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'created_at', '-rating', 'rating']:
        all_reviews = all_reviews.order_by(sort_by)
    
    # Convert to list for response rate calculation
    reviews_list = list(all_reviews)
    total_reviews = len(reviews_list)
    reviews_with_response = sum(1 for review in reviews_list if review.has_response)
    response_rate = (reviews_with_response / total_reviews * 100) if total_reviews > 0 else 0
    
    context = {
        'vendor': vendor,
        'reviews': reviews_list,
        'rating_filter': rating_filter,
        'sort_by': sort_by,
        'total_reviews': total_reviews,
        'reviews_with_response': reviews_with_response,
        'response_rate': response_rate,
    }
    
    return render(request, 'market/vendor_reviews.html', context)

@vendor_team_required()
def respond_to_review(request, vendor_id, review_id):
    """Respond to a review (public or private)"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    review = get_object_or_404(Review, id=review_id, vendor=vendor)
    
    # Check if review already has a response
    existing_response = None
    try:
        existing_response = review.response
    except ReviewResponse.DoesNotExist:
        pass
    
    if request.method == 'POST':
        if existing_response:
            form = ReviewResponseForm(request.POST, instance=existing_response)
        else:
            form = ReviewResponseForm(request.POST)
        
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.vendor = vendor
            response.save()
            
            # If private response, create a message
            if not response.is_public:
                # Try to find the consumer user to send message
                # For now, we'll send email notification
                # In the future, you may want to link reviews to actual User accounts
                try:
                    send_private_review_response_notification(response, review)
                except Exception as e:
                    # Log error but don't fail the response creation
                    # In production, you'd want to log this properly
                    pass
            
            messages.success(request, f'Response saved successfully!')
            return redirect('vendor_reviews', vendor_id=vendor.id)
    else:
        if existing_response:
            form = ReviewResponseForm(instance=existing_response)
        else:
            form = ReviewResponseForm()
    
    context = {
        'vendor': vendor,
        'review': review,
        'form': form,
        'existing_response': existing_response,
    }
    
    return render(request, 'market/review_response.html', context)

@vendor_team_required()
def edit_review_response(request, vendor_id, review_id):
    """Edit or delete a review response"""
    vendor = get_object_or_404(Vendor, id=vendor_id)
    review = get_object_or_404(Review, id=review_id, vendor=vendor)
    
    try:
        response = review.response
    except ReviewResponse.DoesNotExist:
        messages.error(request, 'No response found for this review.')
        return redirect('vendor_reviews', vendor_id=vendor.id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            response.delete()
            messages.success(request, 'Response deleted successfully.')
            return redirect('vendor_reviews', vendor_id=vendor.id)
        else:
            form = ReviewResponseForm(request.POST, instance=response)
            if form.is_valid():
                form.save()
                messages.success(request, 'Response updated successfully!')
                return redirect('vendor_reviews', vendor_id=vendor.id)
    else:
        form = ReviewResponseForm(instance=response)
    
    context = {
        'vendor': vendor,
        'review': review,
        'response': response,
        'form': form,
    }
    
    return render(request, 'market/edit_review_response.html', context)

# User Profile Management
@login_required
def edit_profile(request):
    """Edit user profile - email, name, password, delete account"""
    user = request.user
    
    # Get user's vendors for display
    user_vendors_list = Vendor.objects.filter(team_members__user=user).distinct()
    
    profile_form = UserProfileForm(instance=user)
    password_form = PasswordChangeFormCustom(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'update_profile':
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('edit_profile')
        
        elif action == 'change_password':
            password_form = PasswordChangeFormCustom(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('edit_profile')
        
        elif action == 'delete_account':
            # Delete account confirmation
            username = user.username
            user.delete()
            messages.success(request, f'Account "{username}" has been deleted.')
            return redirect('market_home')
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_vendors': user_vendors_list,
    }
    
    return render(request, 'market/edit_profile.html', context)

@login_required
def vendor_dashboard(request):
    """Comprehensive vendor dashboard with analytics and filters"""
    # Get user's vendors
    user_vendors_list = Vendor.objects.filter(team_members__user=request.user).distinct()
    
    if not user_vendors_list.exists():
        messages.info(request, 'You are not a member of any vendor teams.')
        return redirect('market_home')
    
    # Get selected vendor (from query param or default to first)
    selected_vendor_id = request.GET.get('vendor_id')
    if selected_vendor_id:
        try:
            selected_vendor = user_vendors_list.get(id=selected_vendor_id)
        except Vendor.DoesNotExist:
            selected_vendor = user_vendors_list.first()
    else:
        selected_vendor = user_vendors_list.first()
    
    # Safety check - should never happen, but just in case
    if not selected_vendor:
        messages.error(request, 'No vendor found.')
        return redirect('market_home')
    
    # Get filter parameters
    date_range = request.GET.get('date_range', '30')  # Default: last 30 days
    buyer_state = request.GET.get('buyer_state', '')
    buyer_city = request.GET.get('buyer_city', '')
    category = request.GET.get('category', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Calculate date range
    now = timezone.now()
    if start_date and end_date:
        try:
            start = timezone.datetime.strptime(start_date, '%Y-%m-%d')
            end = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            if timezone.is_naive(start):
                start = timezone.make_aware(start)
            if timezone.is_naive(end):
                end = timezone.make_aware(end)
        except ValueError:
            start = now - timedelta(days=30)
            end = now
    else:
        days = int(date_range) if date_range.isdigit() else 30
        start = now - timedelta(days=days)
        end = now
    
    # Base querysets for selected vendor
    orders_qs = Order.objects.filter(vendor=selected_vendor, created_at__gte=start, created_at__lte=end)
    reviews_qs = Review.objects.filter(vendor=selected_vendor, created_at__gte=start, created_at__lte=end)
    carts_qs = Cart.objects.filter(vendor=selected_vendor, updated_at__gte=start, updated_at__lte=end)
    
    # Apply filters
    if buyer_state:
        orders_qs = orders_qs.filter(buyer_state=buyer_state)
    if buyer_city:
        orders_qs = orders_qs.filter(buyer_city=buyer_city)
    if category:
        orders_qs = orders_qs.filter(items__product_category=category).distinct()
    
    # Calculate overview stats
    total_orders = orders_qs.count()
    completed_orders = orders_qs.filter(status__in=['completed', 'delivered']).count()
    total_revenue = orders_qs.filter(status__in=['completed', 'delivered']).aggregate(
        total=Sum('total_price', output_field=DecimalField())
    )['total'] or Decimal('0.00')
    
    # Potential revenue (from carts) - need to calculate from cart items since total_price is a property
    # Calculate by summing (quantity * product.price) for all cart items in the date range
    cart_items_qs = CartItem.objects.filter(
        cart__vendor=selected_vendor,
        cart__updated_at__gte=start,
        cart__updated_at__lte=end
    )
    potential_revenue = cart_items_qs.aggregate(
        total=Sum(F('quantity') * F('product__price'), output_field=DecimalField())
    )['total'] or Decimal('0.00')
    
    # Reviews stats
    total_reviews = reviews_qs.count()
    avg_rating = reviews_qs.aggregate(avg=Avg('rating'))['avg'] or 0
    reviews_with_responses = reviews_qs.filter(response__isnull=False).count()
    response_rate = (reviews_with_responses / total_reviews * 100) if total_reviews > 0 else 0
    
    # Rating distribution
    rating_distribution = reviews_qs.values('rating').annotate(count=Count('id')).order_by('rating')
    rating_dist = {i: 0 for i in range(1, 6)}
    for item in rating_distribution:
        rating_dist[item['rating']] = item['count']
    
    # Orders by date (for chart) - convert to list with serializable values
    orders_by_date_qs = orders_qs.annotate(date=TruncDate('created_at')).values('date').annotate(
        count=Count('id'),
        revenue=Sum('total_price', filter=Q(status__in=['completed', 'delivered']), output_field=DecimalField())
    ).order_by('date')
    orders_by_date = []
    for item in orders_by_date_qs:
        orders_by_date.append({
            'date': str(item['date']) if item['date'] else '',
            'count': item['count'] or 0,
            'revenue': float(item['revenue'] or 0)
        })
    
    # Orders by category
    orders_by_category_qs = OrderItem.objects.filter(
        order__vendor=selected_vendor,
        order__created_at__gte=start,
        order__created_at__lte=end
    ).values('product_category').annotate(
        count=Count('id'),
        revenue=Sum('subtotal', filter=Q(order__status__in=['completed', 'delivered']), output_field=DecimalField())
    ).order_by('-count')
    orders_by_category = []
    for item in orders_by_category_qs:
        orders_by_category.append({
            'product_category': item['product_category'] or 'Unknown',
            'count': item['count'] or 0,
            'revenue': float(item['revenue'] or 0)
        })
    
    # Orders by location
    orders_by_location_qs = orders_qs.exclude(buyer_state__isnull=True).exclude(buyer_state='').values('buyer_state').annotate(
        count=Count('id'),
        revenue=Sum('total_price', filter=Q(status__in=['completed', 'delivered']), output_field=DecimalField())
    ).order_by('-count')
    orders_by_location = []
    for item in orders_by_location_qs:
        orders_by_location.append({
            'buyer_state': item['buyer_state'] or 'Unknown',
            'count': item['count'] or 0,
            'revenue': float(item['revenue'] or 0)
        })
    
    # Reviews by date
    reviews_by_date_qs = reviews_qs.annotate(date=TruncDate('created_at')).values('date').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('date')
    reviews_by_date = []
    for item in reviews_by_date_qs:
        reviews_by_date.append({
            'date': str(item['date']) if item['date'] else '',
            'count': item['count'] or 0,
            'avg_rating': float(item['avg_rating'] or 0)
        })
    
    # Get unique states and cities for filter dropdowns
    unique_states = Order.objects.filter(vendor=selected_vendor).exclude(buyer_state__isnull=True).exclude(buyer_state='').values_list('buyer_state', flat=True).distinct().order_by('buyer_state')
    unique_cities = Order.objects.filter(vendor=selected_vendor).exclude(buyer_city__isnull=True).exclude(buyer_city='').values_list('buyer_city', flat=True).distinct().order_by('buyer_city')
    
    # Product categories for filter
    categories = Product.CATEGORY_CHOICES
    
    context = {
        'user_vendors_list': user_vendors_list,
        'selected_vendor': selected_vendor,
        'date_range': date_range,
        'buyer_state': buyer_state,
        'buyer_city': buyer_city,
        'category': category,
        'start_date': start_date if start_date else start.strftime('%Y-%m-%d'),
        'end_date': end_date if end_date else end.strftime('%Y-%m-%d'),
        'unique_states': unique_states,
        'unique_cities': unique_cities,
        'categories': categories,
        # Overview stats
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'potential_revenue': potential_revenue,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'response_rate': round(response_rate, 1),
        'rating_distribution': rating_dist,
        # Chart data (already serialized as JSON strings)
        'orders_by_date_json': json.dumps(orders_by_date),
        'orders_by_category_json': json.dumps(orders_by_category),
        'orders_by_location_json': json.dumps(orders_by_location),
        'reviews_by_date_json': json.dumps(reviews_by_date),
    }
    
    return render(request, 'market/vendor_dashboard.html', context)

def login_view(request):
    """Custom login view for all users"""
    if request.user.is_authenticated:
        return redirect('market_home')
    
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_param = request.POST.get('next', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            if next_param:
                return redirect(next_param)
            return redirect('market_home')
        else:
            messages.error(request, 'Invalid username or password.')
            next_url = next_param  # Preserve next URL on error
    
    return render(request, 'market/login.html', {
        'next': next_url
    })

@login_required
def logout_view(request):
    """Logout view with confirmation"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('market_home')

# Create your views here.
