"""
Management command to set up initial data for the Shine store.
Creates default currencies, categories, and sample products.
"""

from django.core.management.base import BaseCommand
from catalog.models import Currency, Category, Product
from moneyed import list_all_currencies, get_currency


class Command(BaseCommand):
    help = 'Sets up initial data for the store including currencies and categories'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...\n')
        
        # Create currencies
        self.create_currencies()
        
        # Create categories
        self.create_categories()
        
        # Create sample products
        self.create_sample_products()
        
        self.stdout.write(self.style.SUCCESS('\nInitial data setup complete!'))
    
    def create_currencies(self):
        """Create currencies using moneyed library with sample exchange rates."""
        # Exchange rates relative to USD (sample rates - should be updated via API in production)
        exchange_rates = {
            'USD': 1.0, 'EUR': 0.92, 'GBP': 0.79, 'JPY': 149.50, 'CAD': 1.36,
            'AUD': 1.53, 'CHF': 0.88, 'CNY': 7.24, 'INR': 83.10, 'BRL': 4.97,
            'MXN': 17.15, 'KRW': 1320.00, 'SGD': 1.34, 'HKD': 7.82, 'NOK': 10.65,
            'SEK': 10.45, 'DKK': 6.88, 'NZD': 1.64, 'ZAR': 18.90, 'RUB': 89.50,
            'TRY': 32.00, 'PLN': 4.02, 'THB': 35.50, 'MYR': 4.72, 'PHP': 56.30,
            'IDR': 15800.00, 'AED': 3.67, 'SAR': 3.75, 'NGN': 1550.00, 'EGP': 30.90,
            'KES': 153.50, 'GHS': 14.80, 'TZS': 2520.00, 'UGX': 3800.00, 'PKR': 280.00,
            'BDT': 110.00, 'VND': 24500.00, 'COP': 4000.00, 'ARS': 870.00, 'CLP': 950.00,
        }
        
        # Priority currencies to always include (sorted by common usage)
        priority_codes = [
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'BRL',
            'MXN', 'KRW', 'SGD', 'HKD', 'NOK', 'SEK', 'DKK', 'NZD', 'ZAR', 'NGN',
            'KES', 'GHS', 'EGP', 'AED', 'SAR', 'PKR', 'BDT', 'PHP', 'THB', 'MYR',
            'IDR', 'VND', 'PLN', 'TRY', 'RUB', 'COP', 'ARS', 'CLP', 'TZS', 'UGX'
        ]
        
        created_count = 0
        for code in priority_codes:
            try:
                moneyed_currency = get_currency(code)
                currency, created = Currency.objects.update_or_create(
                    code=code,
                    defaults={
                        'name': moneyed_currency.name,
                        'symbol': getattr(moneyed_currency, 'symbol', code) or code,
                        'exchange_rate': exchange_rates.get(code, 1.0),
                        'is_active': True
                    }
                )
                if created:
                    created_count += 1
                status = 'Created' if created else 'Updated'
                self.stdout.write(f'  {status} currency: {currency.code} - {currency.name}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Could not create currency {code}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n  Total currencies: {Currency.objects.count()}'))
    
    def create_categories(self):
        """Create product categories."""
        categories = [
            {
                'name': 'Books',
                'slug': 'books',
                'description': 'Beautiful handcrafted books for reading, collecting, and gifting.',
                'icon_class': 'fa-book',
                'display_order': 1
            },
            {
                'name': 'Diaries',
                'slug': 'diaries',
                'description': 'Personal diaries to capture your daily thoughts, dreams, and memories.',
                'icon_class': 'fa-book-open',
                'display_order': 2
            },
            {
                'name': 'Journals',
                'slug': 'journals',
                'description': 'Premium journals for writing, planning, and self-reflection.',
                'icon_class': 'fa-pen-fancy',
                'display_order': 3
            },
            {
                'name': 'Notebooks',
                'slug': 'notebooks',
                'description': 'Quality notebooks for notes, sketches, and creative ideas.',
                'icon_class': 'fa-book-reader',
                'display_order': 4
            },
            {
                'name': 'Sticky Notes',
                'slug': 'sticky-notes',
                'description': 'Colorful and fun sticky notes to keep you organized.',
                'icon_class': 'fa-sticky-note',
                'display_order': 5
            },
        ]
        
        for cat_data in categories:
            category, created = Category.objects.update_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'icon_class': cat_data['icon_class'],
                    'display_order': cat_data['display_order'],
                    'is_active': True
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} category: {category.name}')
    
    def create_sample_products(self):
        """Create sample products for demonstration."""
        # Get categories
        try:
            books = Category.objects.get(slug='books')
            diaries = Category.objects.get(slug='diaries')
            journals = Category.objects.get(slug='journals')
            notebooks = Category.objects.get(slug='notebooks')
            sticky_notes = Category.objects.get(slug='sticky-notes')
        except Category.DoesNotExist:
            self.stdout.write(self.style.WARNING('Categories not found. Skipping sample products.'))
            return
        
        products = [
            # Books
            {
                'name': 'Classic Leather Journal Book',
                'slug': 'classic-leather-journal-book',
                'category': books,
                'description': 'A timeless leather-bound book with premium pages, perfect for those who appreciate craftsmanship and elegance. Each book is hand-stitched with care.',
                'short_description': 'Handcrafted leather book with premium ivory pages.',
                'price': 45.99,
                'cover_type': 'leather',
                'size': 'a5',
                'pages': 200,
                'paper_type': 'Premium Ivory',
                'color': 'Brown',
                'stock': 50,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Vintage Poetry Book',
                'slug': 'vintage-poetry-book',
                'category': books,
                'description': 'A beautifully designed vintage-style book for poetry lovers. Features gilded edges and a ribbon bookmark.',
                'short_description': 'Elegant vintage design with gilded edges.',
                'price': 35.99,
                'sale_price': 29.99,
                'cover_type': 'hardcover',
                'size': 'a5',
                'pages': 150,
                'paper_type': 'Cream',
                'color': 'Burgundy',
                'stock': 30,
                'is_new': True,
            },
            # Diaries
            {
                'name': '2026 Daily Planner Diary',
                'slug': '2026-daily-planner-diary',
                'category': diaries,
                'description': 'Plan your year with our comprehensive daily planner. Includes monthly overviews, weekly spreads, and goal-setting pages.',
                'short_description': 'Complete 2026 planner with monthly and weekly views.',
                'price': 28.99,
                'cover_type': 'hardcover',
                'size': 'a5',
                'pages': 400,
                'paper_type': 'Recycled',
                'color': 'Navy Blue',
                'stock': 100,
                'is_featured': True,
                'is_new': True,
            },
            {
                'name': 'Personal Reflection Diary',
                'slug': 'personal-reflection-diary',
                'category': diaries,
                'description': 'A guided diary with prompts for self-reflection and personal growth. Perfect for mindfulness practice.',
                'short_description': 'Guided prompts for daily reflection.',
                'price': 24.99,
                'cover_type': 'softcover',
                'size': 'a6',
                'pages': 180,
                'paper_type': 'Premium White',
                'color': 'Lavender',
                'stock': 75,
            },
            # Journals
            {
                'name': 'Bullet Journal Dotted',
                'slug': 'bullet-journal-dotted',
                'category': journals,
                'description': 'The perfect bullet journal with dot grid pages for flexible planning, tracking, and creativity. Lay-flat binding for easy writing.',
                'short_description': 'Dot grid pages with lay-flat binding.',
                'price': 22.99,
                'cover_type': 'hardcover',
                'size': 'a5',
                'pages': 256,
                'paper_type': '120gsm Premium',
                'color': 'Black',
                'stock': 120,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Travel Journal',
                'slug': 'travel-journal',
                'category': journals,
                'description': 'Document your adventures with our travel journal. Includes maps, travel tips, and plenty of space for photos and memories.',
                'short_description': 'Perfect companion for your adventures.',
                'price': 19.99,
                'cover_type': 'softcover',
                'size': 'pocket',
                'pages': 128,
                'paper_type': 'Mixed Media',
                'color': 'Kraft Brown',
                'stock': 60,
                'is_new': True,
            },
            {
                'name': 'Gratitude Journal',
                'slug': 'gratitude-journal',
                'category': journals,
                'description': 'Cultivate positivity with our guided gratitude journal. Daily prompts to help you focus on the good things in life.',
                'short_description': 'Daily prompts for practicing gratitude.',
                'price': 18.99,
                'sale_price': 14.99,
                'cover_type': 'hardcover',
                'size': 'a6',
                'pages': 200,
                'paper_type': 'Ivory',
                'color': 'Rose Gold',
                'stock': 45,
            },
            # Notebooks
            {
                'name': 'Classic Spiral Notebook',
                'slug': 'classic-spiral-notebook',
                'category': notebooks,
                'description': 'A reliable spiral-bound notebook with lined pages. Perfect for students, professionals, and anyone who loves to write.',
                'short_description': 'Durable spiral binding with lined pages.',
                'price': 12.99,
                'cover_type': 'spiral',
                'size': 'a4',
                'pages': 200,
                'paper_type': 'Standard White',
                'color': 'Red',
                'stock': 200,
                'is_bestseller': True,
            },
            {
                'name': 'Sketch Notebook',
                'slug': 'sketch-notebook',
                'category': notebooks,
                'description': 'Heavyweight blank pages perfect for sketching, drawing, and mixed media art. Acid-free paper for archival quality.',
                'short_description': 'Heavyweight blank pages for artists.',
                'price': 16.99,
                'cover_type': 'hardcover',
                'size': 'a5',
                'pages': 120,
                'paper_type': '180gsm Drawing',
                'color': 'Black',
                'stock': 80,
            },
            {
                'name': 'Eco-Friendly Notebook Set',
                'slug': 'eco-friendly-notebook-set',
                'category': notebooks,
                'description': 'Set of 3 eco-friendly notebooks made from 100% recycled materials. Great for everyday notes and organization.',
                'short_description': 'Set of 3 recycled paper notebooks.',
                'price': 15.99,
                'cover_type': 'softcover',
                'size': 'a5',
                'pages': 80,
                'paper_type': '100% Recycled',
                'color': 'Assorted',
                'stock': 150,
                'is_new': True,
            },
            # Sticky Notes
            {
                'name': 'Pastel Sticky Notes Pack',
                'slug': 'pastel-sticky-notes-pack',
                'category': sticky_notes,
                'description': 'A vibrant pack of pastel sticky notes in various sizes and shapes. Perfect for reminders, bookmarks, and decoration.',
                'short_description': '500 sheets in 5 pastel colors.',
                'price': 8.99,
                'color': 'Pastel Mix',
                'stock': 300,
                'is_featured': True,
            },
            {
                'name': 'Transparent Sticky Notes',
                'slug': 'transparent-sticky-notes',
                'category': sticky_notes,
                'description': 'See-through sticky notes that highlight without covering text. Perfect for textbooks and documents.',
                'short_description': '200 transparent sheets in 4 colors.',
                'price': 6.99,
                'color': 'Transparent Mix',
                'stock': 250,
                'is_new': True,
            },
            {
                'name': 'Shaped Sticky Notes Collection',
                'slug': 'shaped-sticky-notes-collection',
                'category': sticky_notes,
                'description': 'Fun shaped sticky notes including hearts, stars, arrows, and speech bubbles. Great for adding personality to your notes.',
                'short_description': 'Fun shapes for creative note-taking.',
                'price': 9.99,
                'sale_price': 7.99,
                'color': 'Assorted',
                'stock': 180,
            },
        ]
        
        for prod_data in products:
            product, created = Product.objects.update_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'category': prod_data['category'],
                    'description': prod_data['description'],
                    'short_description': prod_data.get('short_description', ''),
                    'price': prod_data['price'],
                    'sale_price': prod_data.get('sale_price'),
                    'cover_type': prod_data.get('cover_type', ''),
                    'size': prod_data.get('size', ''),
                    'pages': prod_data.get('pages'),
                    'paper_type': prod_data.get('paper_type', ''),
                    'color': prod_data.get('color', ''),
                    'stock': prod_data.get('stock', 0),
                    'is_available': True,
                    'is_featured': prod_data.get('is_featured', False),
                    'is_new': prod_data.get('is_new', False),
                    'is_bestseller': prod_data.get('is_bestseller', False),
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} product: {product.name}')
