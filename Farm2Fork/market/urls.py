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
    # Vendor Application
    path('apply-to-be-vendor/', views.apply_to_be_vendor, name='apply_to_be_vendor'),
    # Vendor Team Management
    path('vendor/<int:vendor_id>/team/', views.vendor_team_list, name='vendor_team_list'),
    path('vendor/<int:vendor_id>/team/add/', views.add_team_member, name='add_team_member'),
    path('vendor/<int:vendor_id>/team/remove/<int:user_id>/', views.remove_team_member, name='remove_team_member'),
    # Vendor Profile Management
    path('vendor/<int:vendor_id>/edit/', views.edit_vendor_profile, name='edit_vendor_profile'),
    # Product Management
    path('vendor/<int:vendor_id>/products/', views.vendor_products_list, name='vendor_products_list'),
    path('vendor/<int:vendor_id>/products/create/', views.create_product, name='create_product'),
    path('vendor/<int:vendor_id>/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('vendor/<int:vendor_id>/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('vendor/<int:vendor_id>/products/bulk/', views.bulk_product_operations, name='bulk_product_operations'),
    # Review Management
    path('vendor/<int:vendor_id>/reviews/', views.vendor_reviews, name='vendor_reviews'),
    path('vendor/<int:vendor_id>/reviews/<int:review_id>/respond/', views.respond_to_review, name='respond_to_review'),
    path('vendor/<int:vendor_id>/reviews/<int:review_id>/response/edit/', views.edit_review_response, name='edit_review_response'),
    # User Profile Management
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Vendor Dashboard (placeholder for Phase 6)
    path('vendor-dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]