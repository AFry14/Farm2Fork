from django.shortcuts import render
from market.models import Product

# Create your views here.
def go_home(request):
    return render(request, 'home.html')