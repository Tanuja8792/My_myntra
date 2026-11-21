# My Myntra — Django Fashion E-commerce Demo

A responsive Django fashion-store project for learning and portfolio demonstration. It is inspired by common fashion e-commerce workflows and is **not affiliated with Myntra**.

## Included features

- Four collections: Ethnic Wear, Western Wear, Men's Fashion and Accessories
- 200 demo products (50 per collection), with descriptions, prices, discounts, sizes, colours, stock and ratings
- Product-type-specific real photo downloader (Unsplash API; unique photo ID per product)
- Product search, category browsing, filters, sorting and pagination
- Product details, related products and customer reviews
- Registration, login, logout, password-reset pages, profile and address book
- Session cart, wishlist, coupons and Cash on Delivery demo checkout
- Order history, status timeline, cancellation, return and exchange requests
- Admin dashboard, Django Admin, inventory and coupon management
- Order email notification hooks, recent views and a simple style-help endpoint
- CSRF protection and Django password hashing

## Windows setup

Open Command Prompt in the project folder:

```bat
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py seed_products
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Add 200 real product photographs

The project uses Unsplash photographs rather than generated illustrations or random image URLs. Unsplash requires a free API key:

1. Create an Unsplash developer account, register a new application from the developer dashboard, and copy its Access Key. Read the official [Unsplash API documentation](https://unsplash.com/documentation) for the registration steps.
2. In Command Prompt, run `copy .env.example .env`, then run `notepad .env` to edit it. (If `.env` already exists, keep your existing settings and only add the key.)
3. Add your key to `.env`:

```env
UNSPLASH_ACCESS_KEY=your_key_here
```

4. Install dependencies (already included in `requirements.txt`) and run:

```bat
python manage.py fetch_product_images
```

The downloader searches by product type (for example, saree, kurti, men's shirt, handbag and sneakers), assigns a different Unsplash photo ID to each product, stores photographer/source credits in `static/images/products/photo_credits.json`, and uses the official Unsplash image URLs directly. Unsplash requires hotlinked image URLs and photographer attribution; the project displays a photographer credit below each product image.

To replace all previously downloaded photos:

```bat
python manage.py fetch_product_images --force
```

Do not publish your `.env` file or API key. Photo search results are selected automatically; review each image for relevance before using the catalogue commercially. Unsplash demo applications have a 50 API-request-per-hour limit, so the downloader is designed to make a limited number of category/type searches. Follow the Unsplash API guidelines and photo license.

## Email and payments

- The default email backend writes messages to the console. Configure Gmail SMTP in `.env` with an app password if you want actual email delivery.
- Checkout is **Cash on Delivery demo only**. UPI/cards/Google Pay/PhonePe/Paytm are not connected. Add a payment gateway and verify server-side payment callbacks before accepting real payments.
- Delivery statuses are updated by the store administrator; no courier tracking API is connected.

## Before production deployment

Set a strong `SECRET_KEY`, `DEBUG=False`, production `ALLOWED_HOSTS`, HTTPS, secure cookies, a production database, media/static hosting, backups, rate limits, privacy/terms pages and automated tests. This is a portfolio/demo project and should be security-reviewed before real customer use.
