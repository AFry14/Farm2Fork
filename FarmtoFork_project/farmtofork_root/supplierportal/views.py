from django.shortcuts import render
from .forms import VendorRegistrationForm
from .models import Supplier

# Create your views here.
def register_supplier(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'supplier_registration_success.html')
    else:
        form = VendorRegistrationForm()
    return render(request, 'supplier_registration.html', {'form': form})

def supplier_home(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_home.html', {'suppliers': suppliers})