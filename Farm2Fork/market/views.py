from django.shortcuts import render
from .models import Product, Vendor, Consumer

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
