/**
 * Shine Stationery - Main JavaScript
 * Modern E-commerce Interactions & Animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 50,
            delay: 100,
        });
    }

    // Initialize all modules
    initNavbar();
    initSearch();
    initBackToTop();
    initCurrencySelector();
    initProductCards();
    initFilters();
    initSmoothScroll();
    initNewsletterForms();
    initLoadingStates();
});

/**
 * Navbar scroll effects
 */
function initNavbar() {
    const navbar = document.getElementById('mainNavbar');
    if (!navbar) return;

    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        // Add/remove scrolled class
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        // Hide/show navbar on scroll
        if (currentScroll > lastScroll && currentScroll > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });
}

/**
 * Search overlay functionality
 */
function initSearch() {
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.querySelector('.search-input');

    if (!searchToggle || !searchOverlay) return;

    searchToggle.addEventListener('click', () => {
        searchOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        if (searchInput) {
            setTimeout(() => searchInput.focus(), 300);
        }
    });

    const closeSearch = () => {
        searchOverlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    if (searchClose) {
        searchClose.addEventListener('click', closeSearch);
    }

    searchOverlay.addEventListener('click', (e) => {
        if (e.target === searchOverlay) {
            closeSearch();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            closeSearch();
        }
    });
}

/**
 * Back to top button
 */
function initBackToTop() {
    const backToTop = document.getElementById('backToTop');
    if (!backToTop) return;

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 500) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });

    backToTop.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Currency selector - AJAX currency switching
 */
function initCurrencySelector() {
    const currencyOptions = document.querySelectorAll('.currency-option');
    
    currencyOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            
            const currencyCode = this.dataset.currency;
            if (!currencyCode) return;

            // Show loading state
            const btn = document.querySelector('.btn-currency');
            const originalText = btn.textContent;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            btn.disabled = true;

            // Send AJAX request to change currency
            fetch('/api/set-currency/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: `currency=${currencyCode}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to show new prices
                    window.location.reload();
                } else {
                    throw new Error(data.error || 'Failed to change currency');
                }
            })
            .catch(error => {
                console.error('Currency change error:', error);
                btn.textContent = originalText;
                btn.disabled = false;
                showNotification('Failed to change currency. Please try again.', 'error');
            });
        });
    });
}

/**
 * Product card interactions
 */
function initProductCards() {
    // Quick view buttons
    const quickViewBtns = document.querySelectorAll('.quick-view-btn');
    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.dataset.productId;
            // For now, just navigate to product page
            // Could be enhanced with a modal quick view
            console.log('Quick view for product:', productId);
        });
    });

    // Add to Cart buttons (product cards)
    const addToCartBtns = document.querySelectorAll('.product-card .add-to-cart-btn');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            addToCart(productId, 1);
        });
    });

    // Wishlist buttons
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const icon = this.querySelector('i');
            const isAdding = icon.classList.contains('far');
            
            toggleWishlist(productId, isAdding, icon, this);
        });
    });

    // Product card hover effects with touch support
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        // Add touch support for mobile
        card.addEventListener('touchstart', function() {
            this.classList.add('touch-hover');
        });
        
        card.addEventListener('touchend', function() {
            setTimeout(() => this.classList.remove('touch-hover'), 300);
        });
    });
}

/**
 * Add product to cart via AJAX
 */
function addToCart(productId, quantity = 1, customization = null) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    if (customization) {
        formData.append('customization', JSON.stringify(customization));
    }
    
    fetch('/cart/add/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            updateCartCount(data.cart_count);
        } else {
            showNotification(data.error || 'Error adding to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    });
}

/**
 * Toggle wishlist status via AJAX
 */
function toggleWishlist(productId, isAdding, icon, button) {
    const url = isAdding ? '/wishlist/add/' : '/wishlist/remove/';
    const formData = new FormData();
    formData.append('product_id', productId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (isAdding) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                button.style.color = '#ec4899';
                showNotification('Added to wishlist!', 'success');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                button.style.color = '';
                showNotification('Removed from wishlist', 'info');
            }
            updateWishlistCount(data.wishlist_count);
        } else {
            showNotification(data.error || 'Error updating wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating wishlist', 'error');
    });
}

/**
 * Update cart count in navbar
 */
function updateCartCount(count) {
    const cartCountEls = document.querySelectorAll('.cart-count, #cartCount');
    cartCountEls.forEach(el => {
        el.textContent = count;
        el.style.display = count > 0 ? 'flex' : 'none';
    });
}

/**
 * Update wishlist count in navbar
 */
function updateWishlistCount(count) {
    const wishlistCountEls = document.querySelectorAll('.wishlist-count, #wishlistCount');
    wishlistCountEls.forEach(el => {
        el.textContent = count;
        el.style.display = count > 0 ? 'flex' : 'none';
    });
}

/**
 * Filters sidebar functionality
 */
function initFilters() {
    const filtersToggle = document.getElementById('filtersToggle');
    const filtersSidebar = document.getElementById('filtersSidebar');
    
    if (filtersToggle && filtersSidebar) {
        filtersToggle.addEventListener('click', () => {
            filtersSidebar.classList.toggle('active');
            document.body.style.overflow = filtersSidebar.classList.contains('active') ? 'hidden' : '';
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (filtersSidebar.classList.contains('active') && 
                !filtersSidebar.contains(e.target) && 
                !filtersToggle.contains(e.target)) {
                filtersSidebar.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // Apply filters button
    const applyFiltersBtn = document.querySelector('.apply-filters-btn');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }

    // View toggle (grid/list)
    const viewBtns = document.querySelectorAll('.view-btn');
    const productsGrid = document.getElementById('productsGrid');
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const view = this.dataset.view;
            if (productsGrid) {
                if (view === 'list') {
                    productsGrid.classList.add('list-view');
                } else {
                    productsGrid.classList.remove('list-view');
                }
            }
        });
    });
}

/**
 * Apply filters from sidebar
 */
function applyFilters() {
    const url = new URL(window.location);
    
    // Get selected categories
    const categories = document.querySelectorAll('input[name="category"]:checked');
    url.searchParams.delete('category');
    categories.forEach(cat => {
        url.searchParams.append('category', cat.value);
    });
    
    // Get price range
    const minPrice = document.getElementById('minPrice');
    const maxPrice = document.getElementById('maxPrice');
    
    if (minPrice && minPrice.value) {
        url.searchParams.set('min_price', minPrice.value);
    } else {
        url.searchParams.delete('min_price');
    }
    
    if (maxPrice && maxPrice.value) {
        url.searchParams.set('max_price', maxPrice.value);
    } else {
        url.searchParams.delete('max_price');
    }
    
    // Get cover types
    const coverTypes = document.querySelectorAll('input[name="cover_type"]:checked');
    url.searchParams.delete('cover_type');
    coverTypes.forEach(type => {
        url.searchParams.append('cover_type', type.value);
    });
    
    window.location = url;
}

/**
 * Smooth scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const offset = 100; // Account for fixed navbar
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Newsletter form submissions
 */
function initNewsletterForms() {
    const newsletterForms = document.querySelectorAll('.newsletter-form, .newsletter-form-large');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (!emailInput || !emailInput.value) return;
            
            // Show loading state
            const originalContent = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;
            
            // Simulate API call (replace with actual endpoint)
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check"></i>';
                submitBtn.classList.add('btn-success');
                emailInput.value = '';
                
                showNotification('Thank you for subscribing!', 'success');
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalContent;
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('btn-success');
                }, 2000);
            }, 1000);
        });
    });
}

/**
 * Loading states for buttons and forms
 */
function initLoadingStates() {
    // Add loading state to forms on submit
    document.querySelectorAll('form:not(.no-loading)').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.dataset.originalContent = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                submitBtn.disabled = true;
            }
        });
    });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification-toast');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 15px;
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;
    
    // Add animation keyframes if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            .notification-close:hover {
                opacity: 1;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Auto close after 5 seconds
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

function closeNotification(notification) {
    notification.style.animation = 'slideOutRight 0.3s ease forwards';
    setTimeout(() => notification.remove(), 300);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#6366f1'
    };
    return colors[type] || colors.info;
}

/**
 * Parallax effect for hero section
 */
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroShapes = document.querySelectorAll('.hero-shape');
    
    heroShapes.forEach((shape, index) => {
        const speed = 0.2 + (index * 0.1);
        shape.style.transform = `translateY(${scrolled * speed}px)`;
    });
});

/**
 * Image lazy loading helper
 */
function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        // Native lazy loading supported
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback with Intersection Observer
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

/**
 * Debounce helper function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Price formatting helper
 */
function formatPrice(price, currencySymbol = '$') {
    return `${currencySymbol}${parseFloat(price).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`;
}

// Export functions for use in other scripts
window.ShineStore = {
    showNotification,
    formatPrice,
    applyFilters,
    debounce
};
