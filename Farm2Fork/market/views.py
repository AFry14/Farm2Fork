from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from .models import Product, Vendor, Consumer, Review

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
    
    # Filter by price range if specified
    if min_price or max_price:
        filtered_vendors = []
        for vendor in vendors:
            vendor_products = vendor.products.all()
            if vendor_products.exists():
                prices = [p.price for p in vendor_products]
                vendor_min = min(prices)
                vendor_max = max(prices)
                
                if min_price and vendor_min < float(min_price):
                    continue
                if max_price and vendor_max > float(max_price):
                    continue
                
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
    
    context = {
        'vendors': vendors,
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
    
    context = {
        'vendor': vendor,
        'featured_products': featured_products,
        'products_by_category': products_by_category,
        'reviews': reviews,
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

# Create your views here.
