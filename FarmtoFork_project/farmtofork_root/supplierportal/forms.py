from django import forms
from market.models import Vendor 

class VendorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'email', 'phone_number', 'address', 'city', 'state', 'zipcode', 'vendortype', 'description']