# ZayCho Backend

This project is a small FastAPI backend for the ZayCho app.

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

You can connect a frontend with a simple fetch call:

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
