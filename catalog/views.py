from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Product, Category, Currency, ProductReview,
    Cart, CartItem, Wishlist, Order, OrderItem, 
    DeliveryZone, ContactMessage, CustomizableProduct
)


def home(request):
    """Homepage with featured products and categories."""
    categories = Category.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    new_products = Product.objects.filter(is_new=True, is_available=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True, is_available=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
        'bestsellers': bestsellers,
    }
    return render(request, 'catalog/home.html', context)


def product_list(request):
    """List all products with filtering and sorting."""
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter for customizable products only
    customizable = request.GET.get('customizable')
    if customizable:
        products = products.filter(customizable_options__isnull=False)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Filter by cover type
    cover_type = request.GET.get('cover_type')
    if cover_type:
        products = products.filter(cover_type=cover_type)
    
    # Filter by size
    size = request.GET.get('size')
    if size:
        products = products.filter(size=size)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'catalog/product_list.html', context)


def category_detail(request, slug):
    """Display products in a specific category."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_available=True)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'category': category,
        'products': products,
        'sort_by': sort_by,
    }
    return render(request, 'catalog/category_detail.html', context)


def product_detail(request, slug):
    """Display single product details."""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]
    
    reviews = product.reviews.filter(is_approved=True)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'catalog/product_detail.html', context)


def search(request):
    """Search products."""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_available=True
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'catalog/search_results.html', context)


@require_POST
def set_currency(request):
    """Set user's preferred currency in session."""
    currency_code = request.POST.get('currency', 'USD')
    try:
        currency = Currency.objects.get(code=currency_code, is_active=True)
        request.session['currency'] = currency.code
        return JsonResponse({'success': True, 'currency': currency.code})
    except Currency.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Currency not found'}, status=400)


def get_currencies(request):
    """Get all active currencies for the currency selector."""
    currencies = Currency.objects.filter(is_active=True).values('code', 'name', 'symbol')
    return JsonResponse(list(currencies), safe=False)


@require_POST
def submit_review(request, product_id):
    """Submit a product review."""
    product = get_object_or_404(Product, id=product_id)
    
    name = request.POST.get('name')
    email = request.POST.get('email')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')
    
    if all([name, email, rating, comment]):
        ProductReview.objects.create(
            product=product,
            name=name,
            email=email,
            rating=int(rating),
            comment=comment
        )
        return JsonResponse({'success': True, 'message': 'Review submitted for approval'})
    
    return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)


def about(request):
    """About page."""
    return render(request, 'catalog/about.html')


def contact(request):
    """Contact page with message form."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if all([name, email, subject, message]):
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you! Your message has been sent. We\'ll get back to you soon.')
            return redirect('catalog:contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'catalog/contact.html')


# ============ Cart Functions ============

def get_or_create_cart(request):
    """Get or create a cart for the current session."""
    if not request.session.session_key:
        request.session.create()
    
    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    """Display the shopping cart."""
    cart = get_or_create_cart(request)
    delivery_zones = DeliveryZone.objects.filter(is_active=True)
    
    selected_zone_id = request.session.get('delivery_zone_id')
    selected_zone = None
    if selected_zone_id:
        try:
            selected_zone = DeliveryZone.objects.get(id=selected_zone_id)
        except DeliveryZone.DoesNotExist:
            pass
    
    context = {
        'cart': cart,
        'delivery_zones': delivery_zones,
        'selected_zone': selected_zone,
    }
    return render(request, 'catalog/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add a product to the cart."""
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    customization = request.POST.get('customization')  # JSON string for custom options
    
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = get_or_create_cart(request)
    
    # Parse customization if provided
    custom_data = None
    if customization:
        import json
        try:
            custom_data = json.loads(customization)
        except json.JSONDecodeError:
            custom_data = None
    
    # Check if item already in cart (with same customization)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        customization=custom_data,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart.total_items,
            'cart_subtotal': str(cart.subtotal)
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('catalog:cart')


@require_POST
def update_cart_item(request):
    """Update cart item quantity."""
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart = get_or_create_cart(request)
    
    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.total_items,
            'cart_subtotal': str(cart.subtotal),
            'item_total': str(item.total_price) if quantity > 0 else '0'
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)


@require_POST
def remove_from_cart(request):
    """Remove item from cart."""
    item_id = request.POST.get('item_id')
    cart = get_or_create_cart(request)
    
    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
        product_name = item.product.name
        item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{product_name} removed from cart',
                'cart_count': cart.total_items,
                'cart_subtotal': str(cart.subtotal)
            })
        
        messages.success(request, f'{product_name} removed from cart')
    except CartItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        messages.error(request, 'Item not found')
    
    return redirect('catalog:cart')


def get_cart_count(request):
    """Get cart item count for header display."""
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.total_items})


# ============ Wishlist Functions ============

def get_or_create_wishlist(request):
    """Get or create a wishlist for the current session."""
    if not request.session.session_key:
        request.session.create()
    
    wishlist, created = Wishlist.objects.get_or_create(session_key=request.session.session_key)
    return wishlist


def wishlist_view(request):
    """Display the wishlist."""
    wishlist = get_or_create_wishlist(request)
    
    context = {
        'wishlist': wishlist,
        'products': wishlist.products.all()
    }
    return render(request, 'catalog/wishlist.html', context)


@require_POST
def add_to_wishlist(request):
    """Add a product to the wishlist."""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_or_create_wishlist(request)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        action = 'removed'
        message = f'{product.name} removed from wishlist'
    else:
        wishlist.products.add(product)
        action = 'added'
        message = f'{product.name} added to wishlist'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'message': message,
            'wishlist_count': wishlist.products.count()
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'catalog:home'))


@require_POST
def remove_from_wishlist(request):
    """Remove a product from wishlist."""
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_or_create_wishlist(request)
    
    wishlist.products.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} removed from wishlist',
            'wishlist_count': wishlist.products.count()
        })
    
    messages.success(request, f'{product.name} removed from wishlist')
    return redirect('catalog:wishlist')


def get_wishlist_count(request):
    """Get wishlist item count for header display."""
    wishlist = get_or_create_wishlist(request)
    return JsonResponse({'count': wishlist.products.count()})


# ============ Checkout Functions ============

@login_required
def checkout(request):
    """Checkout page."""
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('catalog:product_list')
    
    delivery_zones = DeliveryZone.objects.filter(is_active=True)
    
    context = {
        'cart': cart,
        'delivery_zones': delivery_zones,
    }
    return render(request, 'catalog/checkout.html', context)


@require_POST
def set_delivery_zone(request):
    """Set delivery zone and calculate fee."""
    zone_id = request.POST.get('zone_id')
    cart = get_or_create_cart(request)
    
    try:
        zone = DeliveryZone.objects.get(id=zone_id, is_active=True)
        request.session['delivery_zone_id'] = zone.id
        delivery_fee = zone.get_delivery_fee(cart.subtotal)
        total = cart.subtotal + delivery_fee
        
        return JsonResponse({
            'success': True,
            'delivery_fee': str(delivery_fee),
            'total': str(total),
            'estimated_days': f"{zone.estimated_days_min}-{zone.estimated_days_max}",
            'free_delivery_threshold': str(zone.min_order_free_delivery) if zone.min_order_free_delivery else None
        })
    except DeliveryZone.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Zone not found'}, status=404)


@login_required
@require_POST
def place_order(request):
    """Place an order."""
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)
    
    # Get form data
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    city = request.POST.get('city')
    state = request.POST.get('state', '')
    postal_code = request.POST.get('postal_code', '')
    country = request.POST.get('country', 'Kenya')
    zone_id = request.POST.get('delivery_zone')
    customer_notes = request.POST.get('notes', '')
    
    # Validate required fields
    required_fields = [first_name, last_name, email, phone, address, city, zone_id]
    if not all(required_fields):
        return JsonResponse({'success': False, 'error': 'Please fill in all required fields'}, status=400)
    
    try:
        zone = DeliveryZone.objects.get(id=zone_id, is_active=True)
    except DeliveryZone.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Please select a delivery zone'}, status=400)
    
    # Get current currency
    currency_code = request.session.get('currency', 'USD')
    try:
        currency = Currency.objects.get(code=currency_code)
        exchange_rate = currency.exchange_rate
    except Currency.DoesNotExist:
        currency_code = 'USD'
        exchange_rate = 1
    
    # Calculate totals
    subtotal = cart.subtotal
    delivery_fee = zone.get_delivery_fee(subtotal)
    total = subtotal + delivery_fee
    
    # Create order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        delivery_zone=zone,
        delivery_fee=delivery_fee,
        subtotal=subtotal,
        total=total,
        currency_code=currency_code,
        exchange_rate=exchange_rate,
        customer_notes=customer_notes,
        status='pending',
        payment_status='pending'  # Will be updated when payment gateway is integrated
    )
    
    # Create order items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.total_price,
            customization=cart_item.customization
        )
    
    # Clear cart
    cart.items.all().delete()
    
    # Clear delivery zone from session
    if 'delivery_zone_id' in request.session:
        del request.session['delivery_zone_id']
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': f'/order-confirmation/{order.order_number}/'
        })
    
    return redirect('catalog:order_confirmation', order_number=order.order_number)


def order_confirmation(request, order_number):
    """Order confirmation page."""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Only allow viewing if session matches (for privacy)
    if order.session_key != request.session.session_key:
        messages.error(request, 'Order not found')
        return redirect('catalog:home')
    
    context = {
        'order': order,
    }
    return render(request, 'catalog/order_confirmation.html', context)


def track_order(request):
    """Track order status."""
    order_number = request.GET.get('order', '')
    order = None
    
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check the order number.')
    
    context = {
        'order': order,
        'order_number': order_number,
    }
    return render(request, 'catalog/track_order.html', context)


# ============ Journal Customization ============

def customize_journal(request, slug):
    """Journal customization page."""
    product = get_object_or_404(Product, slug=slug, is_available=True)
    
    try:
        customizable = product.customizable_options
    except CustomizableProduct.DoesNotExist:
        messages.error(request, 'This product cannot be customized')
        return redirect('catalog:product_detail', slug=slug)
    
    context = {
        'product': product,
        'customizable': customizable,
        'materials': customizable.get_available_materials(),
        'colors': customizable.get_available_colors(),
        'page_types': customizable.get_available_page_types(),
    }
    return render(request, 'catalog/customize_journal.html', context)
