from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from market.models import (
    Vendor, Product, Review, Order, OrderItem, Cart, CartItem,
    ReviewResponse, VendorTeamMember
)


class Command(BaseCommand):
    help = 'Populate the database with test data for the vendor dashboard (orders, reviews, carts)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing orders, carts, and review responses before populating',
        )
        parser.add_argument(
            '--vendor-id',
            type=int,
            help='Specific vendor ID to populate data for (uses first vendor if not specified)',
        )

    def handle(self, *args, **options):
        clear_data = options['clear']
        vendor_id = options.get('vendor_id')
        
        # Get or create a test user
        test_user, created = User.objects.get_or_create(
            username='test_customer',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'Customer'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created test user: {test_user.username}'))
        
        # Get vendor
        if vendor_id:
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Vendor with ID {vendor_id} not found'))
                return
        else:
            vendor = Vendor.objects.first()
            if not vendor:
                self.stdout.write(self.style.ERROR('No vendors found. Please run populate_data first.'))
                return
        
        self.stdout.write(f'Populating dashboard data for vendor: {vendor.name}')
        
        # Clear existing data if requested
        if clear_data:
            self.stdout.write('Clearing existing orders, carts, and review responses...')
            Order.objects.filter(vendor=vendor).delete()
            Cart.objects.filter(vendor=vendor).delete()
            ReviewResponse.objects.filter(vendor=vendor).delete()
        
        # Get products for this vendor
        products = list(Product.objects.filter(vendor=vendor))
        if not products:
            self.stdout.write(self.style.ERROR(f'No products found for {vendor.name}. Please create products first.'))
            return
        
        # Create additional test users for variety
        test_users = [test_user]
        for i in range(1, 6):
            user, _ = User.objects.get_or_create(
                username=f'test_customer_{i}',
                defaults={
                    'email': f'test{i}@example.com',
                    'first_name': f'Test{i}',
                    'last_name': 'Customer'
                }
            )
            if _:
                user.set_password('testpass123')
                user.save()
            test_users.append(user)
        
        # States and cities for variety
        locations = [
            {'state': 'Illinois', 'city': 'Chicago', 'zip': '60601'},
            {'state': 'Illinois', 'city': 'Springfield', 'zip': '62701'},
            {'state': 'Illinois', 'city': 'Peoria', 'zip': '61602'},
            {'state': 'Illinois', 'city': 'Bloomington', 'zip': '61701'},
            {'state': 'Illinois', 'city': 'Champaign', 'zip': '61820'},
            {'state': 'Indiana', 'city': 'Indianapolis', 'zip': '46201'},
            {'state': 'Wisconsin', 'city': 'Madison', 'zip': '53701'},
        ]
        
        # Create orders with various dates (spread over last 90 days)
        self.stdout.write('Creating orders...')
        order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'completed', 'cancelled']
        completed_statuses = ['completed', 'delivered']
        
        orders_created = 0
        for i in range(60):  # Create 60 orders
            # Random date within last 90 days
            days_ago = random.randint(0, 90)
            order_date = timezone.now() - timedelta(days=days_ago)
            
            # Random user and location
            user = random.choice(test_users)
            location = random.choice(locations)
            
            # Random status (weighted towards completed/delivered)
            if random.random() < 0.7:  # 70% chance of completed/delivered
                status = random.choice(completed_statuses)
            else:
                status = random.choice(order_statuses)
            
            # Create order
            order = Order.objects.create(
                user=user,
                vendor=vendor,
                status=status,
                total_price=Decimal('0.00'),  # Will be calculated from items
                buyer_city=location['city'],
                buyer_state=location['state'],
                buyer_zip_code=location['zip'],
                shipping_city=location['city'],
                shipping_state=location['state'],
                shipping_zip_code=location['zip'],
                shipping_address=f"{random.randint(100, 9999)} Test Street",
                created_at=order_date,
                updated_at=order_date,
                completed_at=order_date if status in completed_statuses else None
            )
            
            # Add 1-4 items to each order
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            order_total = Decimal('0.00')
            
            for product in selected_products:
                quantity = random.randint(1, 5)
                unit_price = product.price
                subtotal = Decimal(str(quantity)) * unit_price
                order_total += subtotal
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_category=product.category,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
            
            # Update order total
            order.total_price = order_total
            order.save()
            orders_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {orders_created} orders'))
        
        # Create carts (for potential revenue)
        self.stdout.write('Creating carts...')
        carts_created = 0
        for i in range(15):  # Create 15 active carts
            user = random.choice(test_users)
            cart, created = Cart.objects.get_or_create(
                user=user,
                vendor=vendor,
                defaults={
                    'updated_at': timezone.now() - timedelta(days=random.randint(0, 7))
                }
            )
            
            if created:
                # Add items to cart
                num_items = random.randint(1, 3)
                selected_products = random.sample(products, min(num_items, len(products)))
                
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity
                    )
                carts_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created/updated {carts_created} carts'))
        
        # Create reviews with various dates and ratings
        self.stdout.write('Creating reviews...')
        review_names = [
            'Sarah Johnson', 'Mike Chen', 'Emily Rodriguez', 'David Thompson',
            'Lisa Anderson', 'Robert Kim', 'Jennifer Lee', 'Michael Brown',
            'Amanda White', 'James Wilson', 'Patricia Davis', 'Christopher Martinez'
        ]
        
        reviews_created = 0
        for i in range(40):  # Create 40 reviews
            days_ago = random.randint(0, 120)  # Reviews over last 120 days
            review_date = timezone.now() - timedelta(days=days_ago)
            
            # Rating distribution (more positive reviews)
            rating_weights = [1, 2, 3, 4, 5]
            rating = random.choices(rating_weights, weights=[1, 2, 3, 4, 5])[0]
            
            comments = [
                "Great quality products!",
                "Fast shipping and excellent customer service.",
                "Very satisfied with my purchase.",
                "Good value for money.",
                "Will definitely order again!",
                "Products arrived fresh and well-packaged.",
                "Highly recommend this vendor!",
                "Excellent quality, exceeded expectations.",
                "Good products but shipping was a bit slow.",
                "Decent quality, fair prices.",
            ]
            
            Review.objects.create(
                vendor=vendor,
                consumer_name=random.choice(review_names),
                rating=rating,
                comment=random.choice(comments) if random.random() < 0.8 else None,
                created_at=review_date
            )
            reviews_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {reviews_created} reviews'))
        
        # Create review responses (for response rate metric)
        self.stdout.write('Creating review responses...')
        reviews = Review.objects.filter(vendor=vendor)
        responses_created = 0
        
        # Get or create a vendor team member user for responses
        vendor_user, _ = User.objects.get_or_create(
            username='vendor_user',
            defaults={
                'email': 'vendor@example.com',
                'first_name': 'Vendor',
                'last_name': 'User'
            }
        )
        if _:
            vendor_user.set_password('testpass123')
            vendor_user.save()
            # Add to vendor team
            VendorTeamMember.objects.get_or_create(
                user=vendor_user,
                vendor=vendor,
                defaults={'is_owner': True}
            )
        
        # Respond to ~60% of reviews
        reviews_to_respond = random.sample(list(reviews), min(int(len(reviews) * 0.6), len(reviews)))
        
        for review in reviews_to_respond:
            days_after_review = random.randint(1, 7)
            response_date = review.created_at + timedelta(days=days_after_review)
            
            is_public = random.random() < 0.8  # 80% public, 20% private
            
            ReviewResponse.objects.create(
                review=review,
                vendor=vendor,
                response_text=random.choice([
                    "Thank you for your feedback! We're glad you enjoyed our products.",
                    "We appreciate your review and are happy to hear you're satisfied!",
                    "Thank you for your order! We hope to serve you again soon.",
                    "We value your feedback and are continuously working to improve.",
                    "Thank you for choosing us! Your satisfaction is our priority.",
                ]),
                is_public=is_public,
                created_at=response_date,
                updated_at=response_date
            )
            responses_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {responses_created} review responses'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Dashboard test data populated successfully!'))
        self.stdout.write('='*50)
        self.stdout.write(f'Vendor: {vendor.name}')
        self.stdout.write(f'Total Orders: {Order.objects.filter(vendor=vendor).count()}')
        self.stdout.write(f'Completed Orders: {Order.objects.filter(vendor=vendor, status__in=["completed", "delivered"]).count()}')
        self.stdout.write(f'Active Carts: {Cart.objects.filter(vendor=vendor).count()}')
        self.stdout.write(f'Total Reviews: {Review.objects.filter(vendor=vendor).count()}')
        self.stdout.write(f'Review Responses: {ReviewResponse.objects.filter(vendor=vendor).count()}')
        self.stdout.write('\nTest users created:')
        self.stdout.write(f'  - test_customer (and test_customer_1 through test_customer_5)')
        self.stdout.write(f'  - vendor_user (added to vendor team)')
        self.stdout.write('\nYou can now view the dashboard at: /market/vendor-dashboard/')
        self.stdout.write('Note: All test data can be removed through the Django admin panel.')

