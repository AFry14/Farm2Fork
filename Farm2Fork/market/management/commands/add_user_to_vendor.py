from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from market.models import Vendor, VendorTeamMember


class Command(BaseCommand):
    help = 'Add a user to a vendor team'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to add to vendor team')
        parser.add_argument('--vendor-id', type=int, help='Vendor ID (uses first vendor if not specified)')

    def handle(self, *args, **options):
        username = options['username']
        vendor_id = options.get('vendor_id')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Vendor with ID {vendor_id} not found'))
                return
        else:
            vendor = Vendor.objects.first()
            if not vendor:
                self.stdout.write(self.style.ERROR('No vendors found'))
                return
        
        team_member, created = VendorTeamMember.objects.get_or_create(
            user=user,
            vendor=vendor,
            defaults={'is_owner': False}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Added {username} to {vendor.name} team'))
        else:
            self.stdout.write(self.style.WARNING(f'{username} is already a member of {vendor.name} team'))

