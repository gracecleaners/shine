from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def convert_currency(price, currency):
    """Convert price to the specified currency."""
    if not currency or not price:
        return price
    
    try:
        converted = Decimal(str(price)) * Decimal(str(currency.exchange_rate))
        return round(converted, 2)
    except (TypeError, ValueError):
        return price


@register.simple_tag
def format_price(price, currency):
    """Format price with currency symbol."""
    if not currency or not price:
        return f"${price}"
    
    try:
        converted = Decimal(str(price)) * Decimal(str(currency.exchange_rate))
        formatted = f"{currency.symbol}{converted:,.2f}"
        return formatted
    except (TypeError, ValueError):
        return f"{price}"


@register.filter
def star_range(value):
    """Generate range for star ratings."""
    try:
        return range(int(value))
    except (TypeError, ValueError):
        return range(0)


@register.filter
def empty_star_range(value):
    """Generate range for empty stars."""
    try:
        return range(5 - int(value))
    except (TypeError, ValueError):
        return range(5)
