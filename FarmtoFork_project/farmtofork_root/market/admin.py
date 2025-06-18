from django.contrib import admin
from .models import Vendor, Product, Order, Customer, ZipCode
# Register your models here.
admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Customer)
admin.site.register(ZipCode)