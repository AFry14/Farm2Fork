from .models import (
    Consumer, Product, Vendor, Review, Cart, CartItem, Order, OrderItem,
    VendorApplication, VendorTeamMember, ProductMedia, ReviewResponse, Message
)
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

# Vendor Application Admin
@admin.action(description='Approve selected applications')
def approve_applications(modeladmin, request, queryset):
    """Approve vendor applications and create vendor records"""
    from .models import VendorTeamMember
    
    for application in queryset.filter(status='pending'):
        # Create vendor from application
        vendor = Vendor.objects.create(
            name=application.business_name,
            description=application.description,
            story_mission=application.story_mission,
            email=application.email,
            phone=application.phone,
            address=application.address,
            city=application.city,
            state=application.state,
            zip_code=application.zip_code,
            country=application.country,
            ships_goods=application.ships_goods,
            is_verified=True,
            owner=application.applicant,
            application=application
        )
        
        # Create team member (owner)
        VendorTeamMember.objects.create(
            user=application.applicant,
            vendor=vendor,
            is_owner=True,
            added_by=application.applicant
        )
        
        # Update application status
        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        # Send notifications
        from .utils import send_vendor_approval_notifications
        send_vendor_approval_notifications(vendor, application)

@admin.action(description='Reject selected applications')
def reject_applications(modeladmin, request, queryset):
    """Reject vendor applications"""
    for application in queryset.filter(status='pending'):
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save()
        
        # Send rejection notification
        from .utils import send_vendor_rejection_notification
        send_vendor_rejection_notification(application)

class VendorApplicationAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'applicant', 'status', 'created_at', 'reviewed_at', 'actions_column']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['business_name', 'applicant__username', 'applicant__email', 'email']
    readonly_fields = ['applicant', 'created_at', 'updated_at', 'reviewed_by', 'reviewed_at']
    fieldsets = (
        ('Application Information', {
            'fields': ('applicant', 'business_name', 'status', 'created_at', 'updated_at')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Business Details', {
            'fields': ('description', 'story_mission', 'ships_goods')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )
    actions = [approve_applications, reject_applications]
    
    def actions_column(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<span style="color: #28a745;">Pending Review</span>'
            )
        elif obj.status == 'approved':
            return format_html(
                '<span style="color: #28a745;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">✗ Rejected</span>'
            )
    actions_column.short_description = 'Status'

# Vendor Team Member Admin (inline)
class VendorTeamMemberInline(admin.TabularInline):
    model = VendorTeamMember
    extra = 1
    fields = ['user', 'is_owner', 'joined_at', 'added_by']
    readonly_fields = ['joined_at']

# Vendor Admin
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'city', 'state', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'ships_goods', 'created_at']
    search_fields = ['name', 'email', 'city', 'state']
    inlines = [VendorTeamMemberInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'story_mission', 'owner', 'application')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Service Information', {
            'fields': ('service_area', 'ships_goods')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'feature_priority')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

# Product Admin
class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1
    fields = ['image', 'is_primary', 'order']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'category', 'price', 'is_available', 'track_inventory', 'stock_quantity']
    list_filter = ['category', 'is_featured', 'is_available', 'track_inventory', 'vendor']
    search_fields = ['name', 'description', 'vendor__name']
    inlines = [ProductMediaInline]
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'description', 'vendor', 'category', 'price')
        }),
        ('Inventory', {
            'fields': ('track_inventory', 'stock_quantity', 'is_available', 'max_quantity')
        }),
        ('Display', {
            'fields': ('is_featured',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

# Review Response Admin
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'vendor', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['review__consumer_name', 'vendor__name', 'response_text']
    readonly_fields = ['created_at', 'updated_at']

# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['subject', 'body', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at', 'read_at']

# Register models
admin.site.register(VendorApplication, VendorApplicationAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(ReviewResponse, ReviewResponseAdmin)
admin.site.register(VendorTeamMember)
admin.site.register(ProductMedia)
admin.site.register(Message, MessageAdmin)
admin.site.register(Consumer)
admin.site.register(Cart)
admin.site.register(CartItem)

# Order Item Admin (inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_category', 'unit_price', 'subtotal', 'created_at']
    fields = ['product', 'product_name', 'product_category', 'quantity', 'unit_price', 'subtotal']

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'vendor', 'status', 'total_price', 'item_count', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at', 'completed_at', 'vendor', 'buyer_state', 'buyer_city']
    search_fields = ['id', 'user__username', 'user__email', 'vendor__name', 'buyer_city', 'buyer_state', 'buyer_zip_code']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'vendor', 'cart', 'status', 'total_price', 'item_count')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_zip_code', 'shipping_country')
        }),
        ('Buyer Location (for analytics)', {
            'fields': ('buyer_city', 'buyer_state', 'buyer_zip_code')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.item_count
    item_count.short_description = 'Items'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)