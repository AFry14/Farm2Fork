from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Vendor, VendorTeamMember

def vendor_team_required(vendor_id_param='vendor_id'):
    """
    Decorator to check if user is a member of the vendor's team.
    Usage: @vendor_team_required() or @vendor_team_required('vendor_id')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Get vendor_id from kwargs
            vendor_id = kwargs.get(vendor_id_param)
            if not vendor_id:
                return HttpResponseForbidden("Vendor ID not provided")
            
            vendor = get_object_or_404(Vendor, id=vendor_id)
            
            # Check if user is admin (admins can access everything)
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Check if user is a team member
            is_team_member = VendorTeamMember.objects.filter(
                user=request.user,
                vendor=vendor
            ).exists()
            
            if not is_team_member:
                return HttpResponseForbidden("You do not have permission to access this vendor's resources.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def vendor_owner_required(vendor_id_param='vendor_id'):
    """
    Decorator to check if user is the owner of the vendor.
    Usage: @vendor_owner_required() or @vendor_owner_required('vendor_id')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Get vendor_id from kwargs
            vendor_id = kwargs.get(vendor_id_param)
            if not vendor_id:
                return HttpResponseForbidden("Vendor ID not provided")
            
            vendor = get_object_or_404(Vendor, id=vendor_id)
            
            # Check if user is admin (admins can access everything)
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Check if user is the owner
            is_owner = VendorTeamMember.objects.filter(
                user=request.user,
                vendor=vendor,
                is_owner=True
            ).exists()
            
            if not is_owner:
                return HttpResponseForbidden("You must be the vendor owner to perform this action.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

