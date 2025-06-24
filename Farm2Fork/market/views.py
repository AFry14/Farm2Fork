from django.shortcuts import render
from .models import Product, Vendor

def product_list(request):
    products = Product.objects.all() #type: ignore
    return render(request, 'market/product_list.html', {'products': products})

def vendor_list(request):
    vendors = Vendor.objects.all() #type: ignore
    return render(request, 'market/vendor_list.html', {'vendors': vendors})

# Create your views here.
