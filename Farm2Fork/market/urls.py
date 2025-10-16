from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_home, name='market_home'),
    path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('products', views.product_list, name='product_list'),
    path('vendors', views.vendor_list, name='vendor_list'),
    path('consumers', views.consumer_list, name='consumer_list'),
]