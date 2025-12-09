from django import template
from ..models import VendorTeamMember, Vendor

register = template.Library()

@register.filter
def is_vendor_team_member(user, vendor):
    """Check if user is a member of the vendor's team"""
    if not user or not user.is_authenticated:
        return False
    return VendorTeamMember.objects.filter(user=user, vendor=vendor).exists()

@register.filter
def is_vendor_owner(user, vendor):
    """Check if user is the owner of the vendor"""
    if not user or not user.is_authenticated:
        return False
    return VendorTeamMember.objects.filter(user=user, vendor=vendor, is_owner=True).exists()

@register.filter
def user_vendors(user):
    """Get all vendors for a user"""
    if not user or not user.is_authenticated:
        return []
    return Vendor.objects.filter(team_members__user=user).distinct()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0

