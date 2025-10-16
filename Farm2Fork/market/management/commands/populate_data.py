from django.core.management.base import BaseCommand
from market.models import Vendor, Product, Review


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample vendors...')
        
        # Create vendors
        vendor1 = Vendor.objects.create(
            name="Green Valley Organic Farm",
            description="Family-owned organic farm specializing in fresh vegetables, herbs, and sustainable farming practices.",
            story_mission="Founded in 1985, we've been committed to sustainable agriculture and providing our community with the freshest organic produce. Our mission is to promote healthy living through chemical-free farming.",
            email="info@greenvalleyfarm.com",
            phone="(555) 123-4567",
            address="123 Farm Road",
            city="Springfield",
            state="Illinois",
            zip_code="62701",
            country="USA",
            service_area="Central Illinois and surrounding counties",
            ships_goods=True,
            is_active=True,
            is_verified=True,
            feature_priority=1
        )

        vendor2 = Vendor.objects.create(
            name="Sunrise Dairy Co.",
            description="Local dairy farm producing fresh milk, cheese, and dairy products from grass-fed cows.",
            story_mission="Three generations of dairy farming excellence. We believe in happy cows, sustainable practices, and the highest quality dairy products.",
            email="contact@sunrisedairy.com",
            phone="(555) 987-6543",
            address="456 Meadow Lane",
            city="Bloomington",
            state="Illinois",
            zip_code="61701",
            country="USA",
            service_area="Central Illinois",
            ships_goods=False,
            is_active=True,
            is_verified=True,
            feature_priority=2
        )

        vendor3 = Vendor.objects.create(
            name="Heritage Meat Company",
            description="Premium grass-fed beef, pasture-raised pork, and free-range chicken from local farms.",
            story_mission="Connecting consumers with high-quality, ethically raised meat. We work directly with local farmers who share our commitment to animal welfare and sustainable practices.",
            email="orders@heritagemeat.com",
            phone="(555) 456-7890",
            address="789 Ranch Road",
            city="Peoria",
            state="Illinois",
            zip_code="61602",
            country="USA",
            service_area="Central and Northern Illinois",
            ships_goods=True,
            is_active=True,
            is_verified=True,
            feature_priority=3
        )

        self.stdout.write('Creating sample products...')

        # Create products for Green Valley Organic Farm
        Product.objects.create(
            name="Organic Tomatoes",
            description="Fresh, vine-ripened organic tomatoes. Perfect for salads, sauces, and canning.",
            price=4.50,
            category="vegetables",
            is_featured=True,
            vendor=vendor1
        )

        Product.objects.create(
            name="Mixed Salad Greens",
            description="A variety of fresh lettuce, spinach, and arugula. Great for healthy salads.",
            price=3.25,
            category="vegetables",
            is_featured=True,
            vendor=vendor1
        )

        Product.objects.create(
            name="Fresh Basil",
            description="Aromatic fresh basil leaves. Perfect for pesto, pasta, and Italian dishes.",
            price=2.75,
            category="herbs",
            vendor=vendor1
        )

        Product.objects.create(
            name="Organic Carrots",
            description="Sweet, crunchy organic carrots. Great for snacking or cooking.",
            price=2.50,
            category="vegetables",
            vendor=vendor1
        )

        # Create products for Sunrise Dairy Co.
        Product.objects.create(
            name="Fresh Whole Milk",
            description="Creamy, fresh whole milk from grass-fed cows. Pasteurized but not homogenized.",
            price=4.00,
            category="dairy",
            is_featured=True,
            vendor=vendor2
        )

        Product.objects.create(
            name="Aged Cheddar Cheese",
            description="Sharp, aged cheddar cheese. Perfect for sandwiches, crackers, or cooking.",
            price=8.50,
            category="dairy",
            is_featured=True,
            vendor=vendor2
        )

        Product.objects.create(
            name="Greek Yogurt",
            description="Thick, creamy Greek yogurt. High in protein and probiotics.",
            price=5.25,
            category="dairy",
            vendor=vendor2
        )

        Product.objects.create(
            name="Fresh Butter",
            description="Rich, creamy butter made from fresh cream. Perfect for baking and cooking.",
            price=6.00,
            category="dairy",
            vendor=vendor2
        )

        # Create products for Heritage Meat Company
        Product.objects.create(
            name="Grass-Fed Ground Beef",
            description="Premium ground beef from grass-fed cattle. Lean, flavorful, and ethically raised.",
            price=12.99,
            category="meat",
            is_featured=True,
            vendor=vendor3
        )

        Product.objects.create(
            name="Pasture-Raised Chicken Breast",
            description="Tender chicken breast from free-range chickens. No antibiotics or hormones.",
            price=15.99,
            category="meat",
            is_featured=True,
            vendor=vendor3
        )

        Product.objects.create(
            name="Heritage Pork Chops",
            description="Thick-cut pork chops from heritage breed pigs. Raised on pasture with natural feed.",
            price=14.99,
            category="meat",
            vendor=vendor3
        )

        Product.objects.create(
            name="Grass-Fed Beef Steaks",
            description="Premium steaks from grass-fed cattle. Aged for maximum tenderness and flavor.",
            price=24.99,
            category="meat",
            vendor=vendor3
        )

        self.stdout.write('Creating sample reviews...')

        # Create reviews
        Review.objects.create(
            vendor=vendor1,
            consumer_name="Sarah Johnson",
            rating=5,
            comment="Amazing organic produce! The tomatoes are the best I've ever had. Great customer service and fast delivery."
        )

        Review.objects.create(
            vendor=vendor1,
            consumer_name="Mike Chen",
            rating=4,
            comment="Really fresh vegetables. The mixed greens stay fresh for days. Will definitely order again."
        )

        Review.objects.create(
            vendor=vendor2,
            consumer_name="Emily Rodriguez",
            rating=5,
            comment="The milk is so creamy and delicious! You can really taste the difference from store-bought milk."
        )

        Review.objects.create(
            vendor=vendor2,
            consumer_name="David Thompson",
            rating=4,
            comment="Great cheese selection. The aged cheddar has amazing flavor. A bit pricey but worth it for the quality."
        )

        Review.objects.create(
            vendor=vendor3,
            consumer_name="Lisa Anderson",
            rating=5,
            comment="Excellent meat quality! The grass-fed beef is so much more flavorful than what I get at the grocery store."
        )

        Review.objects.create(
            vendor=vendor3,
            consumer_name="Robert Kim",
            rating=4,
            comment="Good selection of meat products. The chicken is very tender. Shipping was fast and packaging was excellent."
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(f'Created {Vendor.objects.count()} vendors')
        self.stdout.write(f'Created {Product.objects.count()} products')
        self.stdout.write(f'Created {Review.objects.count()} reviews')
