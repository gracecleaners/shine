from .models import Currency, Cart, Wishlist
from django.conf import settings


def currency_context(request):
    """Add currency information to all templates."""
    currencies = Currency.objects.filter(is_active=True)
    current_currency_code = request.session.get('currency', settings.DEFAULT_CURRENCY)
    
    try:
        current_currency = Currency.objects.get(code=current_currency_code)
    except Currency.DoesNotExist:
        # Fallback to USD or first available currency
        current_currency = currencies.first()
        if current_currency:
            request.session['currency'] = current_currency.code
    
    return {
        'currencies': currencies,
        'current_currency': current_currency,
    }


def cart_wishlist_context(request):
    """Add cart and wishlist counts to all templates."""
    cart_count = 0
    wishlist_count = 0
    
    if request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            pass
        
        try:
            wishlist = Wishlist.objects.get(session_key=request.session.session_key)
            wishlist_count = wishlist.products.count()
        except Wishlist.DoesNotExist:
            pass
    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
