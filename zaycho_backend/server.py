from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/menu")
async def get_menu():
    return [
        {
            "id": 1,
            "name": "ZayCho Sneakers",
            "price": 45000.0,
            "category": "Fashion",
            "image_url": "https://picsum.photos/200",
            "description": "High quality sneakers"
        },
        {
            "id": 2,
            "name": "ZayCho Lipstick",
            "price": 15000.0,
            "category": "Beauty",
            "image_url": "https://picsum.photos/201",
            "description": "Long lasting color"
        },
        {
            "id": 3,
            "name": "ZayCho Earbuds",
            "price": 35000.0,
            "category": "Gadgets",
            "image_url": "https://picsum.photos/202",
            "description": "Clear sound quality"
        }
    ]

class ChatRequest(BaseModel):
    prompt: str

@app.post("/agent")
async def ask_agent(request: ChatRequest):
    return {"reply": "မင်္ဂလာပါ၊ ZayCho မှ ကူညီရန် အသင့်ရှိပါသည်။"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
