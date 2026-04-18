import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
ASSETS_DIR = BASE_DIR / "assets"
MENU_DATA_FILE = BASE_DIR / "data" / "menu_items.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@lru_cache
def load_menu_items():
    return json.loads(MENU_DATA_FILE.read_text(encoding="utf-8"))


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/menu")
async def get_menu(
    category: str = Query(None, description="Filter by category"),
    search: str = Query(None, description="Search by product name, category, or description"),
):
    menu_items = load_menu_items()

    if category:
        menu_items = [item for item in menu_items if item["category"] == category]

    if search:
        query = search.casefold()
        menu_items = [
            item
            for item in menu_items
            if query in item["name"].casefold()
            or query in item["category"].casefold()
            or query in item["description"].casefold()
        ]

    return menu_items


@app.get("/menu/categories")
async def get_menu_categories():
    categories = sorted({item["category"] for item in load_menu_items()})
    return categories


class ChatRequest(BaseModel):
    prompt: str


@app.post("/agent")
async def ask_agent(request: ChatRequest):
    return {"reply": "မင်္ဂလာပါ၊ ZayCho မှ ကူညီရန် အသင့်ရှိပါသည်။"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
