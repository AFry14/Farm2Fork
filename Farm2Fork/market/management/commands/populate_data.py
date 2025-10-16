from django.core.management.base import BaseCommand
from market.models import Vendor, Product, Review


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample vendors...')
        
        # Clear existing data
        Vendor.objects.all().delete()
        Product.objects.all().delete()
        Review.objects.all().delete()
        
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

        vendor4 = Vendor.objects.create(
            name="Budget Fresh Market",
            description="Affordable fresh produce for budget-conscious families. Quality vegetables and fruits at everyday low prices.",
            story_mission="Making fresh, healthy food accessible to everyone. We believe good nutrition shouldn't break the bank.",
            email="info@budgetfresh.com",
            phone="(555) 321-0987",
            address="100 Main Street",
            city="Decatur",
            state="Illinois",
            zip_code="62523",
            country="USA",
            service_area="Central Illinois",
            ships_goods=False,
            is_active=True,
            is_verified=True,
            feature_priority=4
        )

        vendor5 = Vendor.objects.create(
            name="Luxury Artisan Foods",
            description="Premium gourmet products and specialty items for discerning customers. Handcrafted, artisanal quality.",
            story_mission="Crafting exceptional food experiences through traditional methods and premium ingredients. For those who appreciate the finest.",
            email="concierge@luxuryartisan.com",
            phone="(555) 654-3210",
            address="500 Elite Avenue",
            city="Champaign",
            state="Illinois",
            zip_code="61820",
            country="USA",
            service_area="Central Illinois and Chicago area",
            ships_goods=True,
            is_active=True,
            is_verified=True,
            feature_priority=5
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

        # Create products for Budget Fresh Market (Low prices)
        Product.objects.create(
            name="Basic Potatoes",
            description="Fresh russet potatoes. Perfect for baking, mashing, or frying.",
            price=1.99,
            category="vegetables",
            is_featured=True,
            vendor=vendor4
        )

        Product.objects.create(
            name="Standard Onions",
            description="Yellow cooking onions. Essential kitchen staple.",
            price=0.99,
            category="vegetables",
            vendor=vendor4
        )

        Product.objects.create(
            name="Regular Bananas",
            description="Fresh bananas. Great for snacking or baking.",
            price=1.49,
            category="fruits",
            is_featured=True,
            vendor=vendor4
        )

        Product.objects.create(
            name="Basic Lettuce",
            description="Fresh iceberg lettuce. Crisp and refreshing for salads.",
            price=1.25,
            category="vegetables",
            vendor=vendor4
        )

        # Create products for Luxury Artisan Foods (High prices)
        Product.objects.create(
            name="Truffle Oil",
            description="Premium black truffle oil. Imported from Italy. Luxurious finishing oil.",
            price=89.99,
            category="other",
            is_featured=True,
            vendor=vendor5
        )

        Product.objects.create(
            name="Aged Balsamic Vinegar",
            description="25-year aged balsamic vinegar from Modena. Complex, rich flavor.",
            price=149.99,
            category="other",
            is_featured=True,
            vendor=vendor5
        )

        Product.objects.create(
            name="Artisan Cheese Board",
            description="Curated selection of rare cheeses from around the world.",
            price=125.00,
            category="dairy",
            vendor=vendor5
        )

        Product.objects.create(
            name="Wagyu Beef",
            description="Premium A5 Wagyu beef. The finest beef in the world.",
            price=299.99,
            category="meat",
            vendor=vendor5
        )

        Product.objects.create(
            name="Exotic Mushroom Mix",
            description="Seasonal selection of wild foraged mushrooms. Chef's choice varieties.",
            price=45.00,
            category="vegetables",
            vendor=vendor5
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
