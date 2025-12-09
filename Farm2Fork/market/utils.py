from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Vendor, VendorApplication, VendorTeamMember, Message

def send_vendor_approval_notifications(vendor, application):
    """
    Send approval notifications to vendor team members and main contact email
    """
    # Email to main contact email
    subject = f"Your Vendor Application Has Been Approved - {vendor.name}"
    message = f"""
Hello,

Great news! Your vendor application for "{vendor.name}" has been approved.

You can now:
- Access your vendor dashboard
- Manage your products
- Respond to reviews
- View analytics

Visit your vendor dashboard to get started.

Thank you for joining Farm2Fork!

Best regards,
The Farm2Fork Team
"""
    
    # Send to main contact email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@farm2fork.com',
        recipient_list=[application.email],
        fail_silently=False,
    )
    
    # Send to all team members (including owner)
    team_members = VendorTeamMember.objects.filter(vendor=vendor)
    for member in team_members:
        if member.user.email:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@farm2fork.com',
                recipient_list=[member.user.email],
                fail_silently=False,
            )
        
        # Create in-app notification (using Django messages or a notification model)
        # For now, we'll use a simple approach - you can enhance this later
        # with a proper Notification model if needed

def send_vendor_rejection_notification(application):
    """
    Send rejection notification to applicant
    """
    subject = "Vendor Application Status Update - Farm2Fork"
    message = f"""
Hello {application.applicant.username},

We regret to inform you that your vendor application for "{application.business_name}" has not been approved at this time.
"""
    
    if application.rejection_reason:
        message += f"\nReason: {application.rejection_reason}\n"
    
    message += """
If you have any questions or would like to discuss this decision, please contact us.

Thank you for your interest in Farm2Fork.

Best regards,
The Farm2Fork Team
"""
    
    recipient_email = application.applicant.email if application.applicant.email else application.email
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@farm2fork.com',
        recipient_list=[recipient_email],
        fail_silently=False,
    )

def send_private_review_response_notification(message_obj, review):
    """
    Send email notification when vendor sends private response to review
    """
    subject = f"Response to your review of {review.vendor.name}"
    
    # Get message preview (first 200 chars)
    preview = message_obj.body[:200] + "..." if len(message_obj.body) > 200 else message_obj.body
    
    message = f"""
Hello {review.consumer_name},

You have received a private response to your review of {review.vendor.name}.

Message Preview:
{preview}

To view the full message, please log in to your Farm2Fork account.

Best regards,
The Farm2Fork Team
"""
    
    # Try to get consumer email - for now, we'll need to handle this based on your Consumer model
    # This is a placeholder - you may need to adjust based on how consumer emails are stored
    recipient_email = None
    # If you have a way to get consumer email from review, use it here
    
    if recipient_email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@farm2fork.com',
            recipient_list=[recipient_email],
            fail_silently=False,
        )

def send_new_message_notification(message_obj):
    """
    Send email notification when a new message is received
    """
    subject = f"New message from {message_obj.sender.username}"
    
    # Get message preview (first 200 chars)
    preview = message_obj.body[:200] + "..." if len(message_obj.body) > 200 else message_obj.body
    
    message = f"""
Hello {message_obj.recipient.username},

You have received a new message from {message_obj.sender.username}.

Subject: {message_obj.subject}

Message Preview:
{preview}

To view the full message, please log in to your Farm2Fork account.

Best regards,
The Farm2Fork Team
"""
    
    if message_obj.recipient.email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@farm2fork.com',
            recipient_list=[message_obj.recipient.email],
            fail_silently=False,
        )

