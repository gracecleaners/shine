from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
from moneyed import list_all_currencies, get_currency
import uuid


class Currency(models.Model):
    """Model for different currencies with exchange rates."""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code (e.g., USD, EUR, GBP)")
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, default='$')
    exchange_rate = models.DecimalField(
        max_digits=12, 
        decimal_places=6, 
        default=1.000000,
        help_text="Exchange rate relative to base currency (USD)"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Currencies"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @classmethod
    def get_all_currency_codes(cls):
        """Get all available ISO currency codes from moneyed library."""
        return [str(c) for c in list_all_currencies()]
    
    @classmethod
    def get_currency_info(cls, code):
        """Get currency info from moneyed library."""
        try:
            currency = get_currency(code)
            return {
                'code': str(currency),
                'name': currency.name,
                'symbol': currency.symbol if hasattr(currency, 'symbol') else code
            }
        except Exception:
            return None


class Category(models.Model):
    """Product categories - Books, Diaries, Journals, Notebooks, Sticky Notes."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon_class = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Font Awesome icon class (e.g., fa-book, fa-sticky-note)"
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Product model for all stationery items."""
    
    COVER_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('softcover', 'Softcover'),
        ('spiral', 'Spiral Bound'),
        ('leather', 'Leather Bound'),
        ('fabric', 'Fabric Cover'),
    ]
    
    SIZE_CHOICES = [
        ('a4', 'A4 (210 x 297 mm)'),
        ('a5', 'A5 (148 x 210 mm)'),
        ('a6', 'A6 (105 x 148 mm)'),
        ('b5', 'B5 (176 x 250 mm)'),
        ('pocket', 'Pocket (90 x 140 mm)'),
        ('square', 'Square (210 x 210 mm)'),
        ('custom', 'Custom Size'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Pricing (base price in USD)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Product attributes
    cover_type = models.CharField(max_length=20, choices=COVER_CHOICES, blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    pages = models.PositiveIntegerField(blank=True, null=True, help_text="Number of pages")
    paper_type = models.CharField(max_length=100, blank=True, help_text="e.g., Ivory, Recycled, Premium")
    color = models.CharField(max_length=50, blank=True)
    
    # Images
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Stock and availability
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def current_price(self):
        """Return sale price if available, otherwise regular price."""
        return self.sale_price if self.sale_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale."""
        if self.sale_price and self.price:
            discount = ((self.price - self.sale_price) / self.price) * 100
            return int(discount)
        return 0
    
    @property
    def is_in_stock(self):
        return self.stock > 0 and self.is_available
    
    def get_price_in_currency(self, currency):
        """Convert price to specified currency."""
        if isinstance(currency, str):
            try:
                currency = Currency.objects.get(code=currency)
            except Currency.DoesNotExist:
                return self.current_price
        return self.current_price * currency.exchange_rate
    
    def get_all_images(self):
        """Return list of all product images."""
        images = [self.main_image]
        for img in [self.image_2, self.image_3, self.image_4]:
            if img:
                images.append(img)
        return images


class ProductReview(models.Model):
    """Customer reviews for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.name} for {self.product.name}"


class DeliveryZone(models.Model):
    """Delivery zones with fees (like Jumia's zone-based delivery)."""
    name = models.CharField(max_length=100, help_text="e.g., Nairobi CBD, Nairobi Suburbs, Rest of Kenya")
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    per_kg_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_order_free_delivery = models.DecimalField(
        max_digits=10, decimal_places=2, 
        blank=True, null=True,
        help_text="Minimum order amount for free delivery"
    )
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Delivery Zone"
        verbose_name_plural = "Delivery Zones"
    
    def __str__(self):
        return f"{self.name} - ${self.base_fee}"
    
    def get_delivery_fee(self, order_total, weight_kg=0):
        """Calculate delivery fee based on order total and weight."""
        if self.min_order_free_delivery and order_total >= self.min_order_free_delivery:
            return Decimal('0.00')
        return self.base_fee + (Decimal(str(weight_kg)) * self.per_kg_fee)


class Cart(models.Model):
    """Shopping cart - session based for guests."""
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.session_key[:8]}..."
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())
    
    def get_total_with_delivery(self, delivery_zone=None):
        if delivery_zone:
            return self.subtotal + delivery_zone.get_delivery_fee(self.subtotal)
        return self.subtotal


class CartItem(models.Model):
    """Individual items in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    customization = models.JSONField(blank=True, null=True, help_text="Custom options for journals")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product', 'customization']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        return self.product.current_price
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Wishlist(models.Model):
    """Wishlist - session based for guests."""
    session_key = models.CharField(max_length=40, unique=True)
    products = models.ManyToManyField(Product, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wishlist {self.session_key[:8]}..."


class Order(models.Model):
    """Customer orders."""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Link to user account
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    session_key = models.CharField(max_length=40)
    
    # Customer details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Shipping address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    
    # Delivery
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Currency used at time of order
    currency_code = models.CharField(max_length=3, default='USD')
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, default=1)
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        import random
        import string
        prefix = 'SH'
        random_part = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{random_part}"
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class OrderItem(models.Model):
    """Individual items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Stored in case product is deleted
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    customization = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class ContactMessage(models.Model):
    """Contact form messages."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class JournalCustomization(models.Model):
    """Custom journal options for customizable products."""
    COVER_MATERIAL_CHOICES = [
        ('standard', 'Standard'),
        ('leather', 'Genuine Leather'),
        ('vegan_leather', 'Vegan Leather'),
        ('fabric', 'Fabric'),
        ('canvas', 'Canvas'),
    ]
    
    PAGE_TYPE_CHOICES = [
        ('blank', 'Blank'),
        ('lined', 'Lined'),
        ('dotted', 'Dotted'),
        ('grid', 'Grid'),
        ('mixed', 'Mixed (Lined + Blank)'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customizations')
    name = models.CharField(max_length=100, help_text="Name for this customization option")
    
    # Customization options
    cover_text = models.CharField(max_length=100, blank=True, help_text="Text to emboss on cover")
    cover_material = models.CharField(max_length=20, choices=COVER_MATERIAL_CHOICES, default='standard')
    cover_color = models.CharField(max_length=50, blank=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPE_CHOICES, default='lined')
    page_count = models.PositiveIntegerField(default=100)
    
    # Pricing adjustments
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class CustomizableProduct(models.Model):
    """Flag products that can be customized."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='customizable_options')
    
    allow_cover_text = models.BooleanField(default=True)
    allow_cover_material = models.BooleanField(default=True)
    allow_cover_color = models.BooleanField(default=True)
    allow_page_type = models.BooleanField(default=True)
    allow_page_count = models.BooleanField(default=False)
    
    # Available options (comma-separated or use JSON for complex options)
    available_materials = models.CharField(max_length=200, default='standard,leather,vegan_leather')
    available_colors = models.CharField(max_length=500, default='Black,Brown,Navy,Burgundy,Forest Green')
    available_page_types = models.CharField(max_length=200, default='blank,lined,dotted,grid')
    
    # Price adjustments per option
    text_emboss_price = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    leather_price = models.DecimalField(max_digits=10, decimal_places=2, default=15.00)
    vegan_leather_price = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    extra_pages_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.05, help_text="Per additional page")
    
    class Meta:
        verbose_name = "Customizable Product"
        verbose_name_plural = "Customizable Products"
    
    def __str__(self):
        return f"Customization options for {self.product.name}"
    
    def get_available_materials(self):
        return [m.strip() for m in self.available_materials.split(',')]
    
    def get_available_colors(self):
        return [c.strip() for c in self.available_colors.split(',')]
    
    def get_available_page_types(self):
        return [p.strip() for p in self.available_page_types.split(',')]
