from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models

from .forms import CustomUserCreationForm, CustomLoginForm, ProfileUpdateForm
from catalog.models import Order


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('catalog:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Angaza, {user.first_name}! Your account has been created.')
            
            # Redirect to next URL if available
            next_url = request.GET.get('next', 'catalog:home')
            return redirect(next_url)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('catalog:home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            
            # Redirect to next URL if available
            next_url = request.GET.get('next', 'catalog:home')
            return redirect(next_url)
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('catalog:home')


@login_required
def profile(request):
    """User profile view."""
    user = request.user
    orders = Order.objects.filter(
        models.Q(user=user) | models.Q(email=user.email)
    ).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'recent_orders': orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def order_history(request):
    """View order history."""
    # Get orders by user or by email for legacy orders
    orders = Order.objects.filter(
        models.Q(user=request.user) | models.Q(email=request.user.email)
    ).order_by('-created_at')
    
    return render(request, 'accounts/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """View single order details."""
    order = Order.objects.filter(
        order_number=order_number
    ).filter(
        models.Q(user=request.user) | models.Q(email=request.user.email)
    ).first()
    
    if not order:
        messages.error(request, 'Order not found.')
        return redirect('accounts:order_history')
    
    return render(request, 'accounts/order_detail.html', {'order': order})