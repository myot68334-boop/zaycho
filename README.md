# Lyra Shop

Lyra Shop is a starter e-commerce app for clothing and cosmetics. It includes a FastAPI backend, SQLite database, account login/register flow, product catalog, cart, checkout, order history, admin dashboard, image upload, Stripe-ready card payments, and delivery tracking.

## Included now

- Fashion + beauty storefront UI
- FastAPI API for products, auth, checkout, orders, and shopping assistant
- SQLite database with seeded catalog data
- Session-based login and register flow
- Cart and checkout flow connected to persistent orders
- Admin product CRUD and order tracking tools
- Account deletion flow and store-policy pages
- Mobile wrapper configuration for iOS and Android store builds

## Main files

- [`zaycho_backend/server.py`](/Users/myothant/Documents/New%20project/zaycho_backend/server.py)
- [`zaycho_backend/database.py`](/Users/myothant/Documents/New%20project/zaycho_backend/database.py)
- [`zaycho_backend/frontend/index.html`](/Users/myothant/Documents/New%20project/zaycho_backend/frontend/index.html)
- [`zaycho_backend/frontend/app.js`](/Users/myothant/Documents/New%20project/zaycho_backend/frontend/app.js)
- [`zaycho_backend/frontend/styles.css`](/Users/myothant/Documents/New%20project/zaycho_backend/frontend/styles.css)

## Run locally

```bash
cd "/Users/myothant/Documents/New project/zaycho_backend"
python3 server.py
```

Then open:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/docs`
- `http://127.0.0.1:8080/healthz`

## Current API

- `GET /api/products`
- `GET /api/categories`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/orders`
- `POST /api/orders`
- `POST /api/assistant`
- `POST /api/payments/intent`
- `GET /api/admin/stats`
- `POST /api/admin/uploads`
- `GET/POST/PUT/DELETE /api/admin/products`
- `GET /api/admin/orders`
- `PATCH /api/admin/orders/{order_id}`

## Next suggested upgrades

- Add webhook-based Stripe payment confirmation
- Add shipment carrier API integration
- Add inventory alerts, coupon management, and analytics
- Replace local file uploads with object storage such as S3 or Cloudflare R2
