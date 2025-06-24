from .models import Consumer, Product, Vendor
from django.contrib import admin

# Register your models here.
admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Consumer)