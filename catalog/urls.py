from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.get_cart_count, name='cart_count'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/count/', views.get_wishlist_count, name='wishlist_count'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/set-delivery/', views.set_delivery_zone, name='set_delivery_zone'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('order-confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('track-order/', views.track_order, name='track_order'),
    
    # Journal Customization
    path('customize/<slug:slug>/', views.customize_journal, name='customize_journal'),
    
    # API endpoints
    path('api/set-currency/', views.set_currency, name='set_currency'),
    path('api/currencies/', views.get_currencies, name='get_currencies'),
    path('api/review/<int:product_id>/', views.submit_review, name='submit_review'),
]
