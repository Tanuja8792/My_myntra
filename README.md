# My Myntra – Fashion E-Commerce Platform

A Django-based fashion shopping website inspired by common e-commerce workflows. Educational project; not affiliated with Myntra.

## Included
- Responsive homepage and navigation for Men, Women, Kids and Home & Living
- Four collections: Ethnic Wear, Western Wear, Men's Fashion and Accessories
- 200 demo products (50 per collection), images, prices, discounts, sizes, colours and stock
- Search, sorting and filters; product details and related items
- Registration, login, logout, profile and address book
- Cart, wishlist, coupons and checkout
- Cash on Delivery demo orders, order history, status timeline and cancellation
- Reviews, return/exchange requests, invoice print page
- Django Admin and custom store dashboard
- Inventory and coupon administration, sales summary
- Email notification hooks; recently viewed and simple recommendations
- Simple fashion-help chatbot endpoint
- CSRF protection, Django password hashing and admin permissions

## Run on Windows
```bat
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```
Visit http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/.

## Database
SQLite works by default. For MySQL, install a compatible MySQL driver and set these environment variables in a local `.env` file:
`DB_ENGINE=django.db.backends.mysql`, `DB_NAME=my_myntra`, `DB_USER=...`, `DB_PASSWORD=...`, `DB_HOST=127.0.0.1`, `DB_PORT=3306`.

## Email
Console email is the default. Gmail SMTP can be configured with `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `EMAIL_HOST=smtp.gmail.com`, `EMAIL_PORT=587`, `EMAIL_USE_TLS=True`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (Google App Password), and `DEFAULT_FROM_EMAIL`. Never commit credentials.

## Payment and delivery limitations
Checkout currently provides Cash on Delivery as an educational demo. UPI/cards/Google Pay/PhonePe/Paytm need a payment provider integration and verified server callbacks. The app never stores card details. Delivery statuses are admin-updated; no courier API is connected. AI suggestions and chatbot are basic demo logic, not a trained AI service.

Before production deployment configure HTTPS, secure cookies, production database, media storage, backups, rate limits, payment verification, email verification, privacy/terms and automated tests.
