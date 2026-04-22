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
    get_app_setting,
    get_user_by_token,
    init_db,
    list_categories,
    list_orders,
    list_products,
    set_app_setting,
    update_order_tracking,
    update_product,
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)


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
    callback_query: dict | None = None


class TelegramTestMessageRequest(BaseModel):
    message: str = Field(min_length=2, max_length=400)
    chat_id: int | None = None


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


def assistant_reply(prompt: str) -> str:
    normalized_prompt = prompt.lower()
    if any(keyword in normalized_prompt for keyword in ["serum", "glow", "skincare", "skin"]):
        return "Skincare အတွက် Dew Reset Serum, Matcha Cloud Cleanser, Midnight Repair Cream ကို routine set အဖြစ်စမ်းကြည့်လို့ကောင်းပါတယ်။"
    if any(keyword in normalized_prompt for keyword in ["lip", "makeup", "cosmetic", "cosmetics"]):
        return "Makeup အတွက် Velvet Bloom Lip Tint, Glow Veil Cushion SPF50, Rose Quartz Blush Duo ကို everyday look set အဖြစ်ရွေးနိုင်ပါတယ်။"
    if any(keyword in normalized_prompt for keyword in ["shirt", "pants", "dress", "fashion", "outfit"]):
        return "Fashion side မှာ Lunar Satin Shirt, Studio Cargo Pants, Weekend Co-ord Set တို့ကို best-selling outfit picks အဖြစ် recommend လုပ်ပါတယ်။"
    return "Category, budget, style, skin concern တို့ထဲက တစ်ခုခုပြောပေးရင် clothing နဲ့ cosmetics items တွေထဲက recommendation ပေးနိုင်ပါတယ်။"


TELEGRAM_LAST_CHAT_KEY = "telegram_last_chat_id"
TELEGRAM_COMMANDS = {
    "/help": "Commands: /start, /help, /menu, /shop",
    "/menu": "Browse featured categories and product picks.",
    "/shop": "Open the live ZayCho storefront.",
}
TELEGRAM_STOP_WORDS = {
    "for",
    "with",
    "from",
    "that",
    "this",
    "under",
    "over",
    "need",
    "want",
    "show",
    "give",
    "some",
    "best",
    "item",
    "items",
    "please",
    "recommend",
    "recommendation",
    "suggest",
    "suggestion",
    "looking",
}
TELEGRAM_CATEGORY_HINTS = {
    "Skincare": {"skincare", "serum", "cleanser", "cream", "skin", "oily", "dry", "acne"},
    "Makeup": {"makeup", "lip", "lips", "lipstick", "lip tint", "cushion", "blush", "cosmetic"},
    "Tops": {"top", "tops", "shirt", "overshirt", "blouse", "tee"},
    "Bottoms": {"bottom", "bottoms", "pants", "trouser", "trousers", "skirt", "jeans"},
    "Sets": {"set", "sets", "outfit", "matching", "coord", "co-ord"},
    "Accessories": {"accessory", "accessories", "bag", "tote", "hijab", "scarf"},
}
TELEGRAM_STYLE_HINTS = {
    "casual": {"casual", "daily", "everyday", "simple", "relaxed"},
    "office": {"office", "work", "smart", "formal", "clean"},
    "feminine": {"cute", "feminine", "soft", "date", "pretty"},
    "street": {"street", "cargo", "edgy", "cool", "oversized"},
    "modest": {"modest", "covered", "hijab", "layered"},
    "gift": {"gift", "present", "surprise"},
}
TELEGRAM_SKIN_HINTS = {
    "oily": {"oily", "oil", "greasy"},
    "dry": {"dry", "dehydrated", "flaky"},
    "sensitive": {"sensitive", "redness", "gentle"},
    "acne": {"acne", "pimple", "breakout"},
    "glow": {"glow", "bright", "dewy"},
}
TELEGRAM_COLOR_HINTS = {
    "black": {"black"},
    "white": {"white", "ivory", "cream"},
    "pink": {"pink", "rose", "petal"},
    "brown": {"brown", "mocha", "taupe", "khaki"},
    "blue": {"blue", "navy"},
    "green": {"green", "sage", "olive", "matcha"},
}


def storefront_url() -> str:
    if PUBLIC_BASE_URL and PUBLIC_BASE_URL != "https://example.com":
        return PUBLIC_BASE_URL.rstrip("/")
    return "http://127.0.0.1:8080"


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


def send_telegram_message(chat_id: int, text: str, reply_markup: dict | None = None) -> dict:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return telegram_api_request("sendMessage", payload)


def extract_budget(prompt: str) -> int | None:
    lowered = prompt.lower()
    patterns = [
        r"under\s+(\d{3,6})",
        r"below\s+(\d{3,6})",
        r"budget\s+(\d{3,6})",
        r"(\d{3,6})\s*(?:yen|jpy|kyat)",
        r"(\d{3,6})\s*အောက်",
    ]
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return int(match.group(1))
    return None


def query_tokens(prompt: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z]{3,}", prompt.lower())
        if token not in TELEGRAM_STOP_WORDS
    ]


def detect_from_map(prompt: str, mapping: dict[str, set[str]]) -> str | None:
    lowered = prompt.lower()
    for label, keywords in mapping.items():
        if any(keyword in lowered for keyword in keywords):
            return label
    return None


def parse_shopping_intent(prompt: str) -> dict:
    return {
        "budget": extract_budget(prompt),
        "category": detect_from_map(prompt, TELEGRAM_CATEGORY_HINTS),
        "style": detect_from_map(prompt, TELEGRAM_STYLE_HINTS),
        "skin_concern": detect_from_map(prompt, TELEGRAM_SKIN_HINTS),
        "color": detect_from_map(prompt, TELEGRAM_COLOR_HINTS),
        "tokens": query_tokens(prompt),
    }


def product_match_score(product: dict, prompt: str, intent: dict) -> int:
    haystack = " ".join(
        [
            product["name"],
            product["category"],
            product["description"],
            " ".join(product["colors"]),
            " ".join(product["sizes"]),
            product["badge"],
        ]
    ).lower()
    score = 0
    for token in intent["tokens"]:
        if token in haystack:
            score += 2
    lowered = prompt.lower()
    category = product["category"].lower()
    budget = intent["budget"]
    if category in lowered:
        score += 4
    if intent["category"] and product["category"].lower() == intent["category"].lower():
        score += 7
    if budget is not None and product["price"] <= budget:
        score += 3
    if budget is not None and product["price"] > budget:
        score -= 2
    if "skincare" in lowered and category == "skincare":
        score += 4
    if "makeup" in lowered and category == "makeup":
        score += 4
    if any(word in lowered for word in ["outfit", "fashion", "shirt", "pants", "dress"]) and category in {"tops", "bottoms", "sets"}:
        score += 4
    if intent["skin_concern"] and category == "skincare":
        if intent["skin_concern"] in haystack:
            score += 5
        if intent["skin_concern"] == "oily" and any(word in haystack for word in ["oil", "clean", "foam", "balance"]):
            score += 4
        if intent["skin_concern"] == "dry" and any(word in haystack for word in ["hyaluronic", "cream", "rich", "repair", "dewy"]):
            score += 4
        if intent["skin_concern"] == "sensitive" and any(word in haystack for word in ["gentle", "calm", "soft"]):
            score += 4
    if intent["style"]:
        if intent["style"] == "office" and any(word in haystack for word in ["satin", "polished", "linen", "structured"]):
            score += 4
        if intent["style"] == "casual" and any(word in haystack for word in ["casual", "daily", "everyday", "weekend"]):
            score += 4
        if intent["style"] == "feminine" and any(word in haystack for word in ["rose", "blush", "soft", "skirt"]):
            score += 4
        if intent["style"] == "street" and any(word in haystack for word in ["cargo", "graphite", "overshirt"]):
            score += 4
        if intent["style"] == "modest" and any(word in haystack for word in ["hijab", "overshirt", "layering", "drape"]):
            score += 4
        if intent["style"] == "gift" and any(word in haystack for word in ["gift", "popular", "editor", "best seller"]):
            score += 4
    if intent["color"] and intent["color"] in haystack:
        score += 3
    return score


def format_product_line(product: dict) -> str:
    return f"• {product['name']} ({product['category']}) - ¥{product['price']}"


def recommended_products(prompt: str, limit: int = 3) -> list[dict]:
    products = list_products()
    intent = parse_shopping_intent(prompt)
    scored = [
        (product_match_score(product, prompt, intent), product)
        for product in products
    ]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: (item[0], item[1]["rating"], -item[1]["price"]), reverse=True)
    return [product for _, product in scored[:limit]]


def category_shop_url(category: str) -> str:
    params = parse.urlencode({"category": category})
    return f"{storefront_url()}/?{params}#catalog"


def menu_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "🧴 Skincare", "callback_data": "category:Skincare"},
                {"text": "💄 Makeup", "callback_data": "category:Makeup"},
            ],
            [
                {"text": "👚 Tops", "callback_data": "category:Tops"},
                {"text": "👖 Bottoms", "callback_data": "category:Bottoms"},
            ],
            [
                {"text": "✨ Sets", "callback_data": "category:Sets"},
                {"text": "👜 Accessories", "callback_data": "category:Accessories"},
            ],
            [
                {"text": "🛍 Shop Now", "url": storefront_url()},
                {"text": "🧭 Help", "callback_data": "command:/help"},
            ],
        ]
    }


def menu_command_reply() -> str:
    featured_by_category: dict[str, dict] = {}
    for product in list_products():
        featured_by_category.setdefault(product["category"], product)

    lines = []
    for category in list_categories():
        product = featured_by_category.get(category)
        if not product:
            continue
        lines.append(f"• {category}: {product['name']} - ¥{product['price']}")

    return (
        "မင်္ဂလာပါရှင်၊ ZayCho menu လေးကို category အလိုက် ကြည့်လို့ရပါပြီ။\n\n"
        "လက်ရှိ popular picks:\n"
        f"{chr(10).join(lines)}\n\n"
        "အောက်က button တွေထဲက category ကိုနှိပ်ပြီး ပိုတိကျတဲ့ recommendation ဆက်ယူနိုင်ပါတယ်။"
    )


def help_command_reply() -> str:
    return (
        "ZayCho shopping assistant ကို ဒီလိုအသုံးပြုနိုင်ပါတယ်ရှင်\n\n"
        "/start - bot မိတ်ဆက်နဲ့ shop link\n"
        "/menu - category menu + featured picks\n"
        "/shop - storefront link\n"
        "/help - အသုံးပြုပုံပြန်ကြည့်ရန်\n\n"
        "မေးခွန်းပုံစံ ဥပမာများ:\n"
        "• oily skin အတွက် skincare under 5000 yen\n"
        "• black office outfit under 8000 yen\n"
        "• gift idea for teenage girl\n\n"
        "budget + category + style + skin concern ထည့်လေလေ recommendation ပိုတိကျလေလေပါ။"
    )


def shop_command_reply() -> str:
    return f"ZayCho shop ကို ဒီ link ကနေ တန်းဝင်လို့ရပါတယ်ရှင်:\n{storefront_url()}"


def telegram_response_payload(text: str, reply_markup: dict | None = None) -> dict:
    return {"text": text, "reply_markup": reply_markup}


def product_recommendation_reply(prompt: str) -> str:
    intent = parse_shopping_intent(prompt)
    picks = recommended_products(prompt)
    if not picks:
        return (
            f"{assistant_reply(prompt)}\n\n"
            "ပိုတိကျတဲ့ item လိုချင်ရင် category, budget, style, skin concern ကို ထပ်ပြောပေးပါရှင်။\n"
            f"Shop link: {storefront_url()}"
        )

    budget = intent["budget"]
    detail_bits = []
    if intent["category"]:
        detail_bits.append(intent["category"])
    if intent["style"]:
        detail_bits.append(intent["style"])
    if intent["skin_concern"]:
        detail_bits.append(intent["skin_concern"])
    if intent["color"]:
        detail_bits.append(intent["color"])

    intro = "ကြည့်လိုက်တော့ ကိုက်မယ့် item လေးတွေ ရွေးပေးထားပါတယ်ရှင်:"
    if budget is not None:
        intro = f"Budget ¥{budget} အတွင်းနဲ့ ကိုက်မယ့် item လေးတွေ ရွေးပေးထားပါတယ်ရှင်:"
    if detail_bits:
        intro = f"{', '.join(detail_bits)} အတွက် ကိုက်မယ့် item လေးတွေ ရွေးပေးထားပါတယ်ရှင်:"

    lines = []
    for product in picks:
        descriptor = f"{product['display_emoji']} {product['name']} - ¥{product['price']}"
        benefit = product["description"]
        lines.append(f"{descriptor}\n  {benefit}")

    return (
        f"{intro}\n\n"
        f"{chr(10).join(lines)}\n\n"
        "ပိုတိကျချင်ရင် budget, color, style, skin concern ကို ထပ်ပြောပေးပါရှင်။\n"
        f"Shop link: {storefront_url()}"
    )


def telegram_reply_from_callback(data: str) -> dict:
    if data.startswith("category:"):
        category = data.split(":", 1)[1]
        text = product_recommendation_reply(f"show {category} recommendations")
        buttons = {
            "inline_keyboard": [
                [
                    {"text": f"🛍 Open {category}", "url": category_shop_url(category)},
                    {"text": "↩️ Back to Menu", "callback_data": "command:/menu"},
                ]
            ]
        }
        return telegram_response_payload(text, buttons)
    if data == "command:/help":
        return telegram_response_payload(help_command_reply(), menu_keyboard())
    if data == "command:/menu":
        return telegram_response_payload(menu_command_reply(), menu_keyboard())
    if data == "command:/shop":
        return telegram_response_payload(shop_command_reply(), {"inline_keyboard": [[{"text": "🛍 Open Storefront", "url": storefront_url()}]]})
    return telegram_response_payload("လိုချင်တဲ့ category ကို ထပ်ရွေးပြီး စမ်းကြည့်ပေးပါရှင်။", menu_keyboard())


def build_telegram_reply(prompt: str) -> dict:
    text = prompt.strip()
    command = text.split()[0].lower() if text.startswith("/") else ""
    if command == "/start":
        return telegram_response_payload(
            (
                "မင်္ဂလာပါရှင်၊ ZayCho shopping assistant မှ ကြိုဆိုပါတယ်။\n\n"
                "Fashion, skincare, makeup item recommendation တွေကို budget, category, style, skin concern နဲ့မေးလို့ရပါတယ်။\n"
                "ဥပမာ - black office outfit under 8000 yen\n\n"
                f"Shop link: {storefront_url()}"
            ),
            menu_keyboard(),
        )
    if command == "/help":
        return telegram_response_payload(help_command_reply(), menu_keyboard())
    if command == "/menu":
        return telegram_response_payload(menu_command_reply(), menu_keyboard())
    if command == "/shop":
        return telegram_response_payload(
            shop_command_reply(),
            {"inline_keyboard": [[{"text": "🛍 Open ZayCho Shop", "url": storefront_url()}]]},
        )
    return telegram_response_payload(product_recommendation_reply(text), menu_keyboard())


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
    last_chat_id = ""
    if telegram_enabled():
        base_url = PUBLIC_BASE_URL.rstrip("/")
        if base_url and base_url != "https://example.com":
            webhook_url = f"{base_url}/api/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
        last_chat_id = get_app_setting(TELEGRAM_LAST_CHAT_KEY, "")
    return {
        "stripe_enabled": stripe_enabled(),
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
        "public_base_url": PUBLIC_BASE_URL,
        "telegram_enabled": telegram_enabled(),
        "telegram_bot_username": TELEGRAM_BOT_USERNAME,
        "telegram_webhook_url": webhook_url,
        "telegram_last_chat_id": last_chat_id,
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
    return {"reply": product_recommendation_reply(payload.prompt)}


@app.get("/api/telegram/config")
async def telegram_config() -> dict:
    webhook_url = ""
    last_chat_id = ""
    if telegram_enabled():
        base_url = PUBLIC_BASE_URL.rstrip("/")
        if base_url and base_url != "https://example.com":
            webhook_url = f"{base_url}/api/telegram/webhook/{TELEGRAM_BOT_TOKEN}"
        last_chat_id = get_app_setting(TELEGRAM_LAST_CHAT_KEY, "")
    return {
        "telegram_enabled": telegram_enabled(),
        "telegram_bot_username": TELEGRAM_BOT_USERNAME,
        "webhook_url": webhook_url,
        "last_chat_id": last_chat_id,
        "commands": list(TELEGRAM_COMMANDS.keys()),
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


@app.post("/api/telegram/test-message")
async def telegram_test_message(
    payload: TelegramTestMessageRequest,
    _: Annotated[dict, Depends(admin_user)],
) -> dict:
    if not telegram_enabled():
        raise HTTPException(status_code=501, detail="Telegram bot is not configured on the server.")

    chat_id = payload.chat_id
    if chat_id is None:
        stored_chat_id = get_app_setting(TELEGRAM_LAST_CHAT_KEY, "")
        if not stored_chat_id:
            raise HTTPException(status_code=400, detail="No recent Telegram chat found yet. Message the bot once, then try again.")
        chat_id = int(stored_chat_id)

    telegram_response = send_telegram_message(chat_id, payload.message.strip(), menu_keyboard())
    return {"ok": telegram_response.get("ok", False), "chat_id": chat_id}


@app.post("/api/telegram/webhook/{token}")
async def telegram_webhook(token: str, payload: TelegramWebhookRequest) -> dict:
    if not telegram_enabled():
        raise HTTPException(status_code=501, detail="Telegram bot is not configured on the server.")
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook token.")

    if payload.callback_query:
        callback = payload.callback_query
        callback_id = callback.get("id")
        data = (callback.get("data") or "").strip()
        chat = ((callback.get("message") or {}).get("chat") or {})
        chat_id = chat.get("id")
        if callback_id:
            telegram_api_request("answerCallbackQuery", {"callback_query_id": callback_id})
        if not chat_id or not data:
            return {"ok": True, "ignored": True}

        set_app_setting(TELEGRAM_LAST_CHAT_KEY, str(chat_id))
        reply_payload = telegram_reply_from_callback(data)
        telegram_response = send_telegram_message(
            chat_id,
            reply_payload["text"],
            reply_payload.get("reply_markup"),
        )
        return {"ok": telegram_response.get("ok", False), "reply": reply_payload["text"], "callback": data}

    message = payload.message or payload.edited_message or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return {"ok": True, "ignored": True}

    set_app_setting(TELEGRAM_LAST_CHAT_KEY, str(chat_id))
    reply_payload = build_telegram_reply(text)
    telegram_response = send_telegram_message(
        chat_id,
        reply_payload["text"],
        reply_payload.get("reply_markup"),
    )
    return {"ok": telegram_response.get("ok", False), "reply": reply_payload["text"]}


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
