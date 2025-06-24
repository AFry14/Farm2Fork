from django.urls import path
from . import views

urlpatterns = [
    path('products', views.product_list, name='product_list'),
    path('vendors', views.vendor_list, name='vendor_list'),
]