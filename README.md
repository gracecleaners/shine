# Shine Stationery - E-commerce Catalog

A modern Django-based e-commerce catalog for stationery products including books, diaries, journals, notebooks, and sticky notes.

## Features

- **Product Management**: Full Django admin interface to manage products, categories, and inventory
- **Multi-Currency Support**: View prices in different currencies (15+ currencies included)
- **Modern Design**: Beautiful, responsive UI with smooth animations
- **Product Categories**: Books, Diaries, Journals, Notebooks, Sticky Notes
- **Product Search**: Full-text search across all products
- **Filtering & Sorting**: Filter by category, price, cover type, and more
- **Product Reviews**: Customer review system with admin moderation
- **SEO Ready**: Meta titles, descriptions, and clean URLs

## Tech Stack

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, Font Awesome, AOS Animations
- **Database**: SQLite (development) / PostgreSQL (production)
- **Template Engine**: Django Templates with custom template tags

## Quick Start

### 1. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations catalog
python manage.py migrate
```

### 4. Create Superuser (for Admin Access)

```bash
python manage.py createsuperuser
```

### 5. Load Initial Data

```bash
python manage.py setup_initial_data
```

This command creates:
- 15 world currencies with exchange rates
- 5 product categories
- 13 sample products

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit:
- **Store**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Project Structure

```
shine/
├── manage.py
├── requirements.txt
├── shine/                      # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── catalog/                    # Main app
│   ├── admin.py               # Admin configuration
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL patterns
│   ├── context_processors.py  # Currency context
│   ├── templatetags/          # Custom template filters
│   └── management/
│       └── commands/          # Management commands
├── templates/                  # HTML templates
│   ├── base.html
│   └── catalog/
│       ├── home.html
│       ├── product_list.html
│       ├── product_detail.html
│       └── ...
├── static/                     # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── media/                      # Uploaded files
    ├── products/
    └── categories/
```

## Admin Guide

### Managing Products

1. Go to Admin → Products
2. Click "Add Product" to create a new product
3. Fill in the required fields:
   - Name, Category, Description
   - Price (in USD - will be converted automatically)
   - Main Image (required for display)
   - Stock quantity
4. Optional fields:
   - Sale Price (for discounts)
   - Cover Type, Size, Pages, Paper Type
   - Additional images
   - SEO fields

### Managing Categories

1. Go to Admin → Categories
2. Create categories with:
   - Name and URL slug
   - Description
   - Icon class (Font Awesome, e.g., `fa-book`)
   - Display order

### Managing Currencies

1. Go to Admin → Currencies
2. Update exchange rates as needed
3. Exchange rates are relative to USD (base currency)
4. Toggle currencies active/inactive

### Moderating Reviews

1. Go to Admin → Product Reviews
2. Check/uncheck "Is approved" to moderate reviews
3. Reviews only appear on the site when approved

## Customization

### Updating Exchange Rates

Exchange rates can be updated manually in the admin or programmatically:

```python
from catalog.models import Currency

# Update a specific currency
eur = Currency.objects.get(code='EUR')
eur.exchange_rate = 0.92
eur.save()
```

### Adding New Currencies

```python
Currency.objects.create(
    code='SEK',
    name='Swedish Krona',
    symbol='kr',
    exchange_rate=10.50,
    is_active=True
)
```

### Styling

Edit `static/css/style.css` to customize:
- Colors (CSS variables at the top)
- Fonts
- Spacing and layouts
- Animations

## Production Deployment

1. Update `settings.py`:
   - Set `DEBUG = False`
   - Add your domain to `ALLOWED_HOSTS`
   - Use a secure `SECRET_KEY`
   - Configure PostgreSQL database
   - Set up static file serving

2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

3. Use a production server:
   ```bash
   pip install gunicorn
   gunicorn shine.wsgi:application
   ```

## API Endpoints

- `POST /api/set-currency/` - Change user's currency preference
- `GET /api/currencies/` - Get list of available currencies
- `POST /api/review/<product_id>/` - Submit a product review

## License

MIT License - Feel free to use and modify for your projects.

## Support

For questions or issues, please open an issue on the repository.
