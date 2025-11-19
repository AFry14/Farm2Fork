from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Min, Max
from django.http import JsonResponse
from .models import Product, Vendor, Consumer, Review, Cart, CartItem

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

# Create your views here.
