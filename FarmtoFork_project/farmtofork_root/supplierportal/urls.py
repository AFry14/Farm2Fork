from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('sadmin/', admin.site.urls),
    path('', views.supplier_home, name='supplier_home'),
    path('register/', views.register_supplier, name='register'),
]