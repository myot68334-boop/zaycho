import base64
import binascii
import json
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from urllib import parse, request

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from database import (
    TRACKING_STEPS,
    UPLOADS_DIR,
    authenticate_user,
    create_order,
    create_product,
    create_session,
    create_user,
    delete_product,
    delete_session,
    delete_user_account,
    get_user_by_token,
    init_db,
    list_categories,
    list_orders,
    list_products,
    update_order_tracking,
    update_product,
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "").strip()
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://example.com").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "").strip()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Lyra Shop API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


class BaseEmailModel(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please provide a valid email address.")
        return email


class RegisterRequest(BaseEmailModel):
    full_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=120)


class LoginRequest(BaseEmailModel):
    password: str = Field(min_length=6, max_length=120)


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=20)


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=5, max_length=30)
    address_line: str = Field(min_length=5, max_length=140)
    city: str = Field(min_length=2, max_length=50)
    payment_method: str = Field(min_length=2, max_length=40)
    payment_status: str = Field(default="Pending", max_length=40)
    payment_provider: str = Field(default="", max_length=40)
    payment_intent_id: str = Field(default="", max_length=120)
    notes: str = Field(default="", max_length=240)
    items: list[OrderItemRequest]


class AssistantRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=240)


class TelegramWebhookRequest(BaseModel):
    update_id: int | None = None
    message: dict | None = None
    edited_message: dict | None = None


class PaymentIntentRequest(BaseModel):
    items: list[OrderItemRequest]
    currency: str = Field(default="jpy", min_length=3, max_length=3)


class UploadImageRequest(BaseModel):
    filename: str = Field(min_length=3, max_length=120)
    content_base64: str = Field(min_length=20)


class ProductPayload(BaseModel):
    sku: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    category: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=10, max_length=400)
    price: int = Field(ge=100, le=1_000_000)
    compare_at_price: int = Field(ge=100, le=1_000_000)
    badge: str = Field(min_length=2, max_length=40)
    inventory: int = Field(ge=0, le=9999)
    rating: float = Field(ge=0, le=5)
    display_emoji: str = Field(min_length=1, max_length=8)
    accent_color: str = Field(min_length=4, max_length=20)
    sizes: list[str]
    colors: list[str]
    image_url: str = Field(default="", max_length=240)


class TrackingUpdateRequest(BaseModel):
    status: str = Field(min_length=2, max_length=40)
    tracking_status: str = Field(min_length=2, max_length=40)
    tracking_number: str = Field(default="", max_length=80)
    note: str = Field(default="", max_length=180)


def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    return authorization.removeprefix("Bearer ").strip()


def current_user(token: Annotated[str, Depends(get_bearer_token)]) -> dict:
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session.")
    return user


def admin_user(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return user


def stripe_enabled() -> bool:
    return bool(STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY)


def sanitize_filename(filename: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "-", filename)
    return cleaned[:120] or "upload.bin"


def stripe_request(endpoint: str, payload: dict[str, str]) -> dict:
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=501, detail="Stripe is not configured on the server.")
    encoded = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        f"https://api.stripe.com/v1/{endpoint}",
        data=encoded,
        headers={
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Stripe request failed: {error}") from error


def telegram_enabled() -> bool:
    return bool(TELEGRAM_BOT_TOKEN)


def telegram_api_request(method: str, payload: dict) -> dict:
    if not telegram_enabled():
        raise HTTPException(status_code=501, detail="Telegram bot is not configured on the server.")

    req = request.Request(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Telegram request failed: {error}") from error


def assistant_reply(prompt: str) -> str:
    normalized_prompt = prompt.lower()
    if any(keyword in normalized_prompt for keyword in ["serum", "glow", "skincare", "skin"]):
        return "Skincare အတွက် Dew Reset Serum, Matcha Cloud Cleanser, Midnight Repair Cream ကို routine set အဖြစ်စမ်းကြည့်လို့ကောင်းပါတယ်။"
    if any(keyword in normalized_prompt for keyword in ["lip", "makeup", "cosmetic", "cosmetics"]):
        return "Makeup အတွက် Velvet Bloom Lip Tint, Glow Veil Cushion SPF50, Rose Quartz Blush Duo ကို everyday look set အဖြစ်ရွေးနိုင်ပါတယ်။"
    if any(keyword in normalized_prompt for keyword in ["shirt", "pants", "dress", "fashion", "outfit"]):
        return "Fashion side မှာ Lunar Satin Shirt, Studio Cargo Pants, Weekend Co-ord Set တို့ကို best-selling outfit picks အဖြစ် recommend လုပ်ပါတယ်။"
    return "Category, budget, style, skin concern တို့ထဲက တစ်ခုခုပြောပေးရင် clothing နဲ့ cosmetics items တွေထဲက recommendation ပေးနိုင်ပါတယ်။"


def build_telegram_reply(prompt: str) -> str:
    if prompt.strip().startswith("/start"):
        base_url = PUBLIC_BASE_URL if PUBLIC_BASE_URL and PUBLIC_BASE_URL != "https://example.com" else "http://127.0.0.1:8080"
        return (
            "မင်္ဂလာပါ၊ ZayCho Telegram bot မှ ကြိုဆိုပါတယ်။\n\n"
            "Product recommendation လိုချင်တာ၊ skincare/fashion item မေးချင်တာတွေကို message ပို့လို့ရပါတယ်။\n"
            f"Shop link: {base_url}"
        )
    return assistant_reply(prompt)


def compute_amount(items: list[OrderItemRequest]) -> int:
    products = {product["id"]: product for product in list_products()}
    subtotal = 0
    for item in items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=400, detail="Selected product no longer exists.")
        subtotal += product["price"] * item.quantity
    shipping = 0 if subtotal >= 12000 else 800
    return subtotal + shipping


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/privacy")
async def privacy_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "privacy.html")


@app.get("/support")
async def support_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "support.html")


@app.get("/account-delete")
async def account_delete_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "account-delete.html")


@app.get("/healthz")
async def healthcheck() -> dict:
    return {"ok": True, "products": len(list_products()), "stripe_enabled": stripe_enabled()}


@app.get("/api/config")
async def config() -> dict:
    webhook_url = ""
    if telegram_enabled():
        base_url = PUBLIC_BASE_URL.rstrip("/")
        if base_url and base_url != "https://example.com":
            webhook_url = f"{base_url}/api/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
    return {
        "stripe_enabled": stripe_enabled(),
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
        "public_base_url": PUBLIC_BASE_URL,
        "telegram_enabled": telegram_enabled(),
        "telegram_bot_username": TELEGRAM_BOT_USERNAME,
        "telegram_webhook_url": webhook_url,
        "tracking_steps": TRACKING_STEPS,
        "default_admin_email": os.getenv("LYRA_ADMIN_EMAIL", "admin@lyrashop.com"),
    }


@app.get("/api/products")
async def get_products(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
) -> list[dict]:
    return list_products(category=category, search=search)


@app.get("/api/categories")
async def get_categories() -> list[str]:
    return list_categories()


@app.post("/api/auth/register")
async def register(payload: RegisterRequest) -> dict:
    try:
        user = create_user(payload.full_name, payload.email, payload.password)
    except Exception as error:
        if "unique" in str(error).lower():
            raise HTTPException(status_code=409, detail="Email already registered.") from error
        raise
    token = create_session(user["id"])
    return {"token": token, "user": user}


@app.post("/api/auth/login")
async def login(payload: LoginRequest) -> dict:
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = create_session(user["id"])
    return {"token": token, "user": user}


@app.get("/api/me")
async def me(user: Annotated[dict, Depends(current_user)]) -> dict:
    return {"user": user}


@app.delete("/api/me")
async def delete_me(
    user: Annotated[dict, Depends(current_user)],
    token: Annotated[str, Depends(get_bearer_token)],
) -> dict:
    delete_user_account(user["id"])
    delete_session(token)
    return {"message": "Account deleted."}


@app.get("/api/orders")
async def orders(user: Annotated[dict, Depends(current_user)]) -> dict:
    return {"orders": list_orders(user["id"])}


@app.post("/api/orders")
async def place_order(
    payload: CheckoutRequest,
    user: Annotated[dict, Depends(current_user)],
) -> dict:
    try:
        order = create_order(
            user_id=user["id"],
            customer_name=payload.customer_name,
            phone=payload.phone,
            address_line=payload.address_line,
            city=payload.city,
            payment_method=payload.payment_method,
            notes=payload.notes,
            items=[item.model_dump() for item in payload.items],
            payment_status=payload.payment_status,
            payment_provider=payload.payment_provider,
            payment_intent_id=payload.payment_intent_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": "Order placed successfully.", "order": order}


@app.post("/api/payments/intent")
async def create_payment_intent(
    payload: PaymentIntentRequest,
    user: Annotated[dict, Depends(current_user)],
) -> dict:
    amount = compute_amount(payload.items)
    response = stripe_request(
        "payment_intents",
        {
            "amount": str(amount),
            "currency": payload.currency.lower(),
            "payment_method_types[]": "card",
            "metadata[user_id]": str(user["id"]),
            "metadata[user_email]": user["email"],
        },
    )
    return {
        "payment_intent_id": response["id"],
        "client_secret": response["client_secret"],
        "amount": amount,
        "currency": payload.currency.lower(),
    }


@app.post("/api/assistant")
async def assistant(payload: AssistantRequest) -> dict:
    return {"reply": assistant_reply(payload.prompt)}


@app.get("/api/telegram/config")
async def telegram_config() -> dict:
    webhook_url = ""
    if telegram_enabled():
        base_url = PUBLIC_BASE_URL.rstrip("/")
        if base_url and base_url != "https://example.com":
            webhook_url = f"{base_url}/api/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
    return {
        "telegram_enabled": telegram_enabled(),
        "telegram_bot_username": TELEGRAM_BOT_USERNAME,
        "webhook_url": webhook_url,
    }


@app.post("/api/telegram/set-webhook")
async def telegram_set_webhook(_: Annotated[dict, Depends(admin_user)]) -> dict:
    if not telegram_enabled():
        raise HTTPException(status_code=501, detail="Telegram bot is not configured on the server.")
    if not PUBLIC_BASE_URL or PUBLIC_BASE_URL == "https://example.com":
        raise HTTPException(status_code=400, detail="Set PUBLIC_BASE_URL before enabling Telegram webhook.")

    webhook_url = f"{PUBLIC_BASE_URL.rstrip('/')}/api/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
    response = telegram_api_request("setWebhook", {"url": webhook_url})
    return {"ok": response.get("ok", False), "webhook_url": webhook_url, "telegram_response": response}


@app.post("/api/telegram/webhook/{token}")
async def telegram_webhook(token: str, payload: TelegramWebhookRequest) -> dict:
    if not telegram_enabled():
        raise HTTPException(status_code=501, detail="Telegram bot is not configured on the server.")
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook token.")

    message = payload.message or payload.edited_message or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return {"ok": True, "ignored": True}

    reply = build_telegram_reply(text)
    telegram_response = telegram_api_request(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": reply,
        },
    )
    return {"ok": telegram_response.get("ok", False), "reply": reply}


@app.get("/api/admin/stats")
async def admin_stats(_: Annotated[dict, Depends(admin_user)]) -> dict:
    products = list_products()
    orders = list_orders()
    revenue = sum(order["total"] for order in orders)
    return {
        "products": len(products),
        "orders": len(orders),
        "revenue": revenue,
        "customers": len({order["user_id"] for order in orders}),
    }


@app.post("/api/admin/uploads")
async def admin_upload_image(
    payload: UploadImageRequest,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    try:
        encoded = payload.content_base64.split(",", 1)[-1]
        content = base64.b64decode(encoded)
    except (binascii.Error, ValueError) as error:
        raise HTTPException(status_code=400, detail="Invalid base64 image content.") from error

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be smaller than 5MB.")

    filename = sanitize_filename(payload.filename)
    target = UPLOADS_DIR / f"{os.urandom(4).hex()}-{filename}"
    target.write_bytes(content)
    return {"url": f"/uploads/{target.name}"}


@app.get("/api/admin/products")
async def admin_products(_: Annotated[dict, Depends(admin_user)]) -> dict:
    return {"products": list_products()}


@app.post("/api/admin/products")
async def admin_create_product(
    payload: ProductPayload,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    try:
        product = create_product(payload.model_dump())
    except Exception as error:
        if "unique" in str(error).lower():
            raise HTTPException(status_code=409, detail="SKU already exists.") from error
        raise
    return {"product": product}


@app.put("/api/admin/products/{product_id}")
async def admin_update_product(
    product_id: int,
    payload: ProductPayload,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    try:
        product = update_product(product_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"product": product}


@app.delete("/api/admin/products/{product_id}")
async def admin_delete_product(
    product_id: int,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    delete_product(product_id)
    return {"message": "Product deleted."}


@app.get("/api/admin/orders")
async def admin_orders(_: Annotated[dict, Depends(admin_user)]) -> dict:
    return {"orders": list_orders()}


@app.patch("/api/admin/orders/{order_id}")
async def admin_update_order(
    order_id: int,
    payload: TrackingUpdateRequest,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    try:
        order = update_order_tracking(
            order_id=order_id,
            status=payload.status,
            tracking_status=payload.tracking_status,
            tracking_number=payload.tracking_number,
            note=payload.note,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"order": order}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
