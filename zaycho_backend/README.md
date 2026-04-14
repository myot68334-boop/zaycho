# ZayCho Backend

This project is a small FastAPI backend for the ZayCho app, and it now serves a lightweight frontend too.

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
- category filters, search, and quick assistant prompts

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
