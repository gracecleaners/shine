from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, Currency, ProductReview,
    DeliveryZone, Cart, CartItem, Wishlist, Order, OrderItem,
    ContactMessage, JournalCustomization, CustomizableProduct
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    list_editable = ['exchange_rate', 'is_active']
    ordering = ['code']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_order', 'is_active', 'product_count', 'image_preview']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 40px; border-radius: 5px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ['name', 'email', 'rating', 'comment', 'created_at']
    can_delete = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'name', 'category', 'price', 'sale_price', 
        'stock', 'is_available', 'is_featured', 'is_new', 'is_bestseller'
    ]
    list_filter = [
        'category', 'is_available', 'is_featured', 'is_new', 
        'is_bestseller', 'cover_type', 'size', 'created_at'
    ]
    search_fields = ['name', 'description', 'short_description']
    list_editable = ['price', 'sale_price', 'stock', 'is_available', 'is_featured', 'is_new', 'is_bestseller']
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [ProductReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Product Details', {
            'fields': ('cover_type', 'size', 'pages', 'paper_type', 'color'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3', 'image_4')
        }),
        ('Inventory & Status', {
            'fields': ('stock', 'is_available', 'is_featured', 'is_new', 'is_bestseller')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.main_image.url
            )
        return '-'
    image_preview.short_description = 'Image'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['name', 'email', 'comment', 'product__name']
    list_editable = ['is_approved']
    ordering = ['-created_at']
    readonly_fields = ['product', 'name', 'email', 'rating', 'comment', 'created_at']


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_fee', 'per_kg_fee', 'min_order_free_delivery', 'estimated_days_min', 'estimated_days_max', 'display_order', 'is_active']
    list_filter = ['is_active']
    list_editable = ['base_fee', 'per_kg_fee', 'is_active', 'display_order']
    ordering = ['display_order', 'name']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'total_items', 'subtotal', 'created_at', 'updated_at']
    readonly_fields = ['session_key', 'total_items', 'subtotal']
    inlines = [CartItemInline]
    ordering = ['-updated_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'product_count', 'created_at']
    filter_horizontal = ['products']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price', 'customization']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'delivery_zone', 'created_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone']
    list_editable = ['status', 'payment_status']
    readonly_fields = ['order_number', 'session_key', 'subtotal', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'payment_status')
        }),
        ('Customer', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'delivery_zone', 'delivery_fee')
        }),
        ('Totals', {
            'fields': ('subtotal', 'total', 'currency_code', 'exchange_rate')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read', 'is_replied']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    ordering = ['-created_at']


class CustomizableProductInline(admin.StackedInline):
    model = CustomizableProduct
    extra = 0


@admin.register(JournalCustomization)
class JournalCustomizationAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'cover_material', 'page_type', 'additional_price', 'is_active']
    list_filter = ['cover_material', 'page_type', 'is_active']
    search_fields = ['product__name', 'name']
    list_editable = ['is_active', 'additional_price']


@admin.register(CustomizableProduct)
class CustomizableProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'allow_cover_text', 'allow_cover_material', 'allow_page_type']
    list_filter = ['allow_cover_text', 'allow_cover_material', 'allow_page_type']
    search_fields = ['product__name']


# Customize admin site
admin.site.site_header = "Shine Stationery Admin"
admin.site.site_title = "Shine Admin Portal"
admin.site.index_title = "Welcome to Shine Stationery Management"
