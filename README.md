# ZayCho

ZayCho is a small FastAPI storefront app that serves both an API and a lightweight frontend from the same project.

## Live project overview

- FastAPI backend for product and assistant endpoints
- Built-in frontend served from FastAPI static files
- Search, category filters, quick prompts, and a simple assistant panel
- Ready for GitHub and simple cloud deployment

## Project structure

```text
zaycho_backend/
  frontend/
    app.js
    index.html
    styles.css
  README.md
  database.py
  requirements.txt
  server.py
```

## Local run

```bash
cd "zaycho_backend"
test_env/bin/python server.py
```

Then open:

- `http://127.0.0.1:8080/`
- `http://127.0.0.1:8080/docs`

## API endpoints

- `GET /menu` returns sample product data
- `POST /agent` returns a sample assistant reply

Example request:

```bash
curl -X POST http://127.0.0.1:8080/agent \
  -H "Content-Type: application/json" \
  -d '{"prompt":"hello"}'
```

## Deployment

This repo includes a [render.yaml](/Users/myothant/Documents/New%20project/render.yaml) file for a simple Render deployment.

The app reads the `PORT` environment variable automatically, so it can run on local machines and cloud platforms.

## Repository

- GitHub: [myot68334-boop/zaycho](https://github.com/myot68334-boop/zaycho)
- App source: [zaycho_backend](/Users/myothant/Documents/New%20project/zaycho_backend)
