# ZayCho Backend

This directory contains the FastAPI app, static frontend files, and deployment-ready backend entrypoint for ZayCho.

## Requirements

- Python 3.14
- A virtual environment with the packages from `requirements.txt`

## Run the app

```bash
cd "/Users/myothant/Documents/New project/zaycho_backend"
test_env/bin/python server.py
```

The app runs on:

- `http://127.0.0.1:8080`

## API docs

When the server is running, open:

- `http://127.0.0.1:8080/docs`
- `http://127.0.0.1:8080/redoc`

## Frontend

When the server is running, open:

- `http://127.0.0.1:8080/`

The homepage shows:

- the product menu from `GET /menu`
- a simple assistant form connected to `POST /agent`
- search, category filters, and quick prompt actions

## Deployment note

The server reads the `PORT` environment variable automatically. That means the same app can run locally and on services like Render without changing the code.

## Telegram bot

You can connect a Telegram bot to the same assistant reply logic.

Required environment variables:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME` (optional, for display only)
- `PUBLIC_BASE_URL` (required for webhook setup on a public deployment)

Telegram endpoints:

- `GET /api/telegram/config`
- `POST /api/telegram/set-webhook`
- `POST /api/telegram/webhook/{token}`

Webhook setup flow:

1. Create a bot with BotFather
2. Set `TELEGRAM_BOT_TOKEN`
3. Set `PUBLIC_BASE_URL` to your live site URL
4. Log in as admin on ZayCho
5. Call `POST /api/telegram/set-webhook`

After that, Telegram messages sent to your bot will receive the same recommendation replies as `/api/assistant`.

## Available endpoints

### `GET /menu`

Returns the sample product list.

### `POST /agent`

Request body:

```json
{
  "prompt": "hello"
}
```

Sample response:

```json
{
  "reply": "မင်္ဂလာပါ၊ ZayCho မှ ကူညီရန် အသင့်ရှိပါသည်။"
}
```

## Frontend connection example

The included frontend uses a simple fetch call like this:

```html
<script>
  async function loadMenu() {
    const response = await fetch("http://127.0.0.1:8080/menu");
    const data = await response.json();
    console.log(data);
  }

  async function askAgent() {
    const response = await fetch("http://127.0.0.1:8080/agent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt: "hello" })
    });

    const data = await response.json();
    console.log(data);
  }
</script>
```
