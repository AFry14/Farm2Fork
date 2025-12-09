from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from .models import VendorApplication, Vendor, Product, ProductMedia, ReviewResponse

class VendorApplicationForm(forms.ModelForm):
    """Form for vendor application submission"""
    
    class Meta:
        model = VendorApplication
        fields = [
            'business_name', 'email', 'phone', 'address', 'city', 
            'state', 'zip_code', 'country', 'description', 
            'story_mission', 'ships_goods'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Business Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(123) 456-7890'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Street Address (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your business...'
            }),
            'story_mission': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us your story and mission...'
            }),
            'ships_goods': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Make all fields required except address
        for field_name, field in self.fields.items():
            if field_name != 'address':
                field.required = True
    
    def clean_business_name(self):
        """Validate that business name is unique"""
        business_name = self.cleaned_data.get('business_name')
        if business_name:
            # Check if vendor with this name already exists
            if Vendor.objects.filter(name=business_name).exists():
                raise forms.ValidationError(
                    "A vendor with this business name already exists. Please choose a different name."
                )
            # Check if there's a pending application with this name
            if VendorApplication.objects.filter(
                business_name=business_name,
                status='pending'
            ).exists():
                raise forms.ValidationError(
                    "An application with this business name is already pending. Please wait for approval or contact support."
                )
        return business_name
    
    def save(self, commit=True):
        """Save the application and link it to the user"""
        application = super().save(commit=False)
        if self.user:
            application.applicant = self.user
        if commit:
            application.save()
        return application

class VendorEditForm(forms.ModelForm):
    """Form for editing vendor profile"""
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'description', 'story_mission', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'country',
            'service_area', 'ships_goods'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Business Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(123) 456-7890'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Street Address (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your business...'
            }),
            'story_mission': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us your story and mission...'
            }),
            'service_area': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Geographic areas where you provide service...'
            }),
            'ships_goods': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_name(self):
        """Validate that business name is unique (excluding current vendor)"""
        name = self.cleaned_data.get('name')
        if name and self.instance:
            # Check if another vendor with this name exists
            if Vendor.objects.filter(name=name).exclude(id=self.instance.id).exists():
                raise forms.ValidationError(
                    "A vendor with this business name already exists. Please choose a different name."
                )
        return name

class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    images = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text="Upload one or more product images (hold Ctrl/Cmd to select multiple)"
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category', 'is_featured',
            'max_quantity', 'track_inventory', 'stock_quantity', 'is_available'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Product description...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'track_inventory': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleInventoryFields()'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'id': 'id_stock_quantity'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.vendor = kwargs.pop('vendor', None)
        super().__init__(*args, **kwargs)
        
        # Set initial value for track_inventory if editing
        if self.instance and self.instance.pk:
            if self.instance.track_inventory:
                self.fields['stock_quantity'].required = True
        else:
            # For new products, stock_quantity is not required initially
            self.fields['stock_quantity'].required = False
    
    def clean(self):
        """Validate inventory tracking requirements"""
        cleaned_data = super().clean()
        track_inventory = cleaned_data.get('track_inventory', False)
        stock_quantity = cleaned_data.get('stock_quantity')
        
        if track_inventory:
            if stock_quantity is None:
                raise forms.ValidationError({
                    'stock_quantity': 'Stock quantity is required when inventory tracking is enabled.'
                })
            if stock_quantity is not None and stock_quantity < 0:
                raise forms.ValidationError({
                    'stock_quantity': 'Stock quantity cannot be negative.'
                })
        
        return cleaned_data
    
    def clean_price(self):
        """Validate price is positive"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price
    
    def save(self, commit=True):
        """Save product and handle images"""
        product = super().save(commit=False)
        if self.vendor:
            product.vendor = self.vendor
        
        if commit:
            product.save()
            # Handle image uploads will be done in the view
        
        return product

class ReviewResponseForm(forms.ModelForm):
    """Form for vendor responses to reviews"""
    
    class Meta:
        model = ReviewResponse
        fields = ['response_text', 'is_public']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'maxlength': 1000,
                'placeholder': 'Enter your response (max 1000 characters)...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['response_text'].required = True
        self.fields['response_text'].widget.attrs['id'] = 'response_text'
    
    def clean_response_text(self):
        """Validate response text length"""
        response_text = self.cleaned_data.get('response_text', '').strip()
        if len(response_text) > 1000:
            raise forms.ValidationError('Response text cannot exceed 1000 characters.')
        if len(response_text) < 1:
            raise forms.ValidationError('Response text is required.')
        return response_text

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

class PasswordChangeFormCustom(PasswordChangeForm):
    """Custom password change form with styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

