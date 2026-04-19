# ZayCho

ZayCho is a Myanmar grocery storefront built on FastAPI with a mobile-first frontend, PWA support, and native iOS/Android wrapper scaffolds for store packaging.

## What is included

- FastAPI backend for menu, category, assistant, and health endpoints
- Mobile storefront frontend served directly from FastAPI
- Wishlist, cart, trend picks, category browsing, and assistant flows
- PWA metadata, install prompt support, and service worker caching
- Native mobile wrapper scaffolds under [`mobile`](/Users/myothant/Documents/New%20project/mobile)
- Render deployment config in [`render.yaml`](/Users/myothant/Documents/New%20project/render.yaml)

## Project structure

```text
zaycho_backend/
  assets/
  data/
  frontend/
    app.js
    index.html
    manifest.webmanifest
    service-worker.js
    styles.css
  scripts/
  requirements.txt
  server.py
mobile/
  ios/
  android/
docs/
  store/
```

## Local run

```bash
cd "/Users/myothant/Documents/New project/zaycho_backend"
test_env/bin/python server.py
```

Open:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/docs`
- `http://127.0.0.1:8080/healthz`

## API endpoints

- `GET /menu`
- `GET /menu/categories`
- `POST /agent`
- `GET /healthz`

Example:

```bash
curl http://127.0.0.1:8080/menu
curl http://127.0.0.1:8080/healthz
```

## Mobile packaging

- iOS wrapper scaffold: [`mobile/ios`](/Users/myothant/Documents/New%20project/mobile/ios)
- Android wrapper scaffold: [`mobile/android`](/Users/myothant/Documents/New%20project/mobile/android)
- Store release notes: [`docs/store`](/Users/myothant/Documents/New%20project/docs/store)

## Deployment

Live web deployment:

- [zaycho.onrender.com](https://zaycho.onrender.com)

Repository:

- [myot68334-boop/zaycho](https://github.com/myot68334-boop/zaycho)
