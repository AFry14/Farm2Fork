from django.urls import path
from . import views

urlpatterns = [
    path('', views.go_home, name='home'),
    #path('about/', views.go_about, name='about'),
    #path('contact/', views.go_contact, name='contact'),
]