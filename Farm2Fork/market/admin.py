from .models import Consumer, Product, Vendor, Review, Cart, CartItem
from django.contrib import admin

# Register your models here.
admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Review)
admin.site.register(Consumer)
admin.site.register(Cart)
admin.site.register(CartItem)