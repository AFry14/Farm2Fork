from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_home, name='market_home'),
    path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),
    path('products', views.product_list, name='product_list'),
    path('vendors', views.vendor_list, name='vendor_list'),
    path('consumers', views.consumer_list, name='consumer_list'),
    # Cart URLs
    path('cart/vendor/<int:vendor_id>/', views.cart_detail, name='cart_detail'),
    path('cart/my-carts/', views.my_carts, name='my_carts'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/<int:vendor_id>/', views.clear_cart, name='clear_cart'),
    path('cart/count/<int:vendor_id>/', views.cart_count, name='cart_count'),
]