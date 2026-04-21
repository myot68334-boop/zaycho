import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "store.db"
UPLOADS_DIR = BASE_DIR / "uploads"

SEED_PRODUCTS = [
    {
        "sku": "TOP-001",
        "name": "Lunar Satin Shirt",
        "category": "Tops",
        "description": "Soft satin shirt with a relaxed silhouette for day-to-night styling.",
        "price": 5900,
        "compare_at_price": 6900,
        "badge": "New Drop",
        "inventory": 18,
        "rating": 4.8,
        "display_emoji": "👚",
        "accent_color": "#f4c7c3",
        "sizes": ["S", "M", "L"],
        "colors": ["Rose", "Ivory", "Black"],
        "image_url": "",
    },
    {
        "sku": "TOP-002",
        "name": "Tokyo Linen Overshirt",
        "category": "Tops",
        "description": "Breathable overshirt designed for layering in warm weather.",
        "price": 6400,
        "compare_at_price": 7600,
        "badge": "Best Seller",
        "inventory": 12,
        "rating": 4.7,
        "display_emoji": "🧥",
        "accent_color": "#b7d3cc",
        "sizes": ["M", "L", "XL"],
        "colors": ["Sage", "Sand"],
        "image_url": "",
    },
    {
        "sku": "BOT-001",
        "name": "Studio Cargo Pants",
        "category": "Bottoms",
        "description": "Structured cargo pants with a tapered fit and lightweight stretch.",
        "price": 7200,
        "compare_at_price": 8200,
        "badge": "Limited",
        "inventory": 16,
        "rating": 4.6,
        "display_emoji": "👖",
        "accent_color": "#c9c2b8",
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Khaki", "Graphite"],
        "image_url": "",
    },
    {
        "sku": "SET-001",
        "name": "Weekend Co-ord Set",
        "category": "Sets",
        "description": "Matching top and skirt set with a polished casual feel.",
        "price": 9800,
        "compare_at_price": 11200,
        "badge": "Bundle",
        "inventory": 8,
        "rating": 4.9,
        "display_emoji": "✨",
        "accent_color": "#f1ddb4",
        "sizes": ["S", "M", "L"],
        "colors": ["Cream", "Mocha"],
        "image_url": "",
    },
    {
        "sku": "MKP-001",
        "name": "Velvet Bloom Lip Tint",
        "category": "Makeup",
        "description": "Long-wear lip tint with a velvet finish and lightweight hydration.",
        "price": 2400,
        "compare_at_price": 2900,
        "badge": "Hot",
        "inventory": 30,
        "rating": 4.8,
        "display_emoji": "💄",
        "accent_color": "#d8818f",
        "sizes": ["One Size"],
        "colors": ["Cherry", "Nude Rose", "Brick"],
        "image_url": "",
    },
    {
        "sku": "SKN-001",
        "name": "Dew Reset Serum",
        "category": "Skincare",
        "description": "Niacinamide and hyaluronic acid serum for balanced, dewy skin.",
        "price": 4200,
        "compare_at_price": 4900,
        "badge": "Restock",
        "inventory": 22,
        "rating": 4.9,
        "display_emoji": "🧴",
        "accent_color": "#9cc9ff",
        "sizes": ["30ml"],
        "colors": ["Clear"],
        "image_url": "",
    },
    {
        "sku": "SKN-002",
        "name": "Matcha Cloud Cleanser",
        "category": "Skincare",
        "description": "Gentle foam cleanser that removes sunscreen and excess oil cleanly.",
        "price": 2800,
        "compare_at_price": 3300,
        "badge": "Daily Pick",
        "inventory": 26,
        "rating": 4.7,
        "display_emoji": "🫧",
        "accent_color": "#9ec79c",
        "sizes": ["120ml"],
        "colors": ["Matcha"],
        "image_url": "",
    },
    {
        "sku": "MKP-002",
        "name": "Glow Veil Cushion SPF50",
        "category": "Makeup",
        "description": "Buildable cushion foundation with glow finish and SPF protection.",
        "price": 4700,
        "compare_at_price": 5200,
        "badge": "Trending",
        "inventory": 14,
        "rating": 4.8,
        "display_emoji": "🌞",
        "accent_color": "#e8c9a4",
        "sizes": ["14g"],
        "colors": ["21 Light", "23 Natural"],
        "image_url": "",
    },
    {
        "sku": "ACC-001",
        "name": "Silk Touch Hijab",
        "category": "Accessories",
        "description": "Smooth drape hijab fabric with subtle sheen for elegant everyday looks.",
        "price": 3600,
        "compare_at_price": 4300,
        "badge": "Popular",
        "inventory": 20,
        "rating": 4.6,
        "display_emoji": "🧕",
        "accent_color": "#cab0de",
        "sizes": ["Free Size"],
        "colors": ["Dusty Pink", "Taupe", "Navy"],
        "image_url": "",
    },
    {
        "sku": "ACC-002",
        "name": "Everyday Canvas Tote",
        "category": "Accessories",
        "description": "Oversized tote for cosmetics, books, and daily essentials.",
        "price": 3100,
        "compare_at_price": 3600,
        "badge": "Gift Pick",
        "inventory": 25,
        "rating": 4.5,
        "display_emoji": "👜",
        "accent_color": "#bfa58f",
        "sizes": ["Free Size"],
        "colors": ["Natural", "Olive"],
        "image_url": "",
    },
    {
        "sku": "MKP-003",
        "name": "Rose Quartz Blush Duo",
        "category": "Makeup",
        "description": "Two-tone blush compact for fresh everyday color.",
        "price": 2600,
        "compare_at_price": 3100,
        "badge": "Editor Pick",
        "inventory": 18,
        "rating": 4.7,
        "display_emoji": "🌸",
        "accent_color": "#f1a9ba",
        "sizes": ["8g"],
        "colors": ["Petal", "Coral"],
        "image_url": "",
    },
    {
        "sku": "SKN-003",
        "name": "Midnight Repair Cream",
        "category": "Skincare",
        "description": "Rich overnight cream with ceramide support for dry or tired skin.",
        "price": 5300,
        "compare_at_price": 6100,
        "badge": "Night Care",
        "inventory": 10,
        "rating": 4.9,
        "display_emoji": "🌙",
        "accent_color": "#7f95c4",
        "sizes": ["50ml"],
        "colors": ["Blue"],
        "image_url": "",
    },
]

TRACKING_STEPS = ["Pending", "Paid", "Packed", "Shipped", "Delivered"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, _ = password_hash.split("$", 1)
    return hash_password(password, salt) == password_hash


def ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    existing = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def row_to_product(row: sqlite3.Row) -> dict:
    product = dict(row)
    product["sizes"] = json.loads(product["sizes"])
    product["colors"] = json.loads(product["colors"])
    return product


def row_to_order(connection: sqlite3.Connection, row: sqlite3.Row) -> dict:
    order = dict(row)
    order["tracking_history"] = json.loads(order["tracking_history"] or "[]")
    items = connection.execute(
        "SELECT product_id, product_name, unit_price, quantity FROM order_items WHERE order_id = ?",
        (order["id"],),
    ).fetchall()
    order["items"] = [dict(item) for item in items]
    return order


def sanitize_user(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "role": row["role"],
        "created_at": row["created_at"],
    }


def init_db() -> None:
    UPLOADS_DIR.mkdir(exist_ok=True)
    connection = get_connection()
    with connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                compare_at_price INTEGER NOT NULL,
                badge TEXT NOT NULL,
                inventory INTEGER NOT NULL,
                rating REAL NOT NULL,
                display_emoji TEXT NOT NULL,
                accent_color TEXT NOT NULL,
                sizes TEXT NOT NULL,
                colors TEXT NOT NULL,
                image_url TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_number TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address_line TEXT NOT NULL,
                city TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'Pending',
                payment_provider TEXT NOT NULL DEFAULT '',
                payment_intent_id TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                subtotal INTEGER NOT NULL,
                shipping_fee INTEGER NOT NULL,
                total INTEGER NOT NULL,
                status TEXT NOT NULL,
                tracking_number TEXT NOT NULL DEFAULT '',
                tracking_status TEXT NOT NULL DEFAULT 'Pending',
                tracking_history TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                unit_price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """
        )

        ensure_column(connection, "users", "role", "TEXT NOT NULL DEFAULT 'customer'")
        ensure_column(connection, "products", "image_url", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "orders", "payment_status", "TEXT NOT NULL DEFAULT 'Pending'")
        ensure_column(connection, "orders", "payment_provider", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "orders", "payment_intent_id", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "orders", "tracking_number", "TEXT NOT NULL DEFAULT ''")
        ensure_column(connection, "orders", "tracking_status", "TEXT NOT NULL DEFAULT 'Pending'")
        ensure_column(connection, "orders", "tracking_history", "TEXT NOT NULL DEFAULT '[]'")

        product_count = connection.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if product_count == 0:
            connection.executemany(
                """
                INSERT INTO products (
                    sku, name, category, description, price, compare_at_price, badge, inventory,
                    rating, display_emoji, accent_color, sizes, colors, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["sku"],
                        item["name"],
                        item["category"],
                        item["description"],
                        item["price"],
                        item["compare_at_price"],
                        item["badge"],
                        item["inventory"],
                        item["rating"],
                        item["display_emoji"],
                        item["accent_color"],
                        json.dumps(item["sizes"]),
                        json.dumps(item["colors"]),
                        item["image_url"],
                    )
                    for item in SEED_PRODUCTS
                ],
            )

        ensure_default_admin(connection)
    connection.close()


def ensure_default_admin(connection: sqlite3.Connection) -> None:
    admin_email = os.getenv("LYRA_ADMIN_EMAIL", "admin@lyrashop.com").strip().lower()
    admin_password = os.getenv("LYRA_ADMIN_PASSWORD", "Admin123!")
    existing = connection.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
    if existing:
        connection.execute("UPDATE users SET role = 'admin' WHERE email = ?", (admin_email,))
        return

    connection.execute(
        """
        INSERT INTO users (full_name, email, password_hash, role, created_at)
        VALUES (?, ?, ?, 'admin', ?)
        """,
        ("Lyra Admin", admin_email, hash_password(admin_password), utc_now()),
    )


def list_products(category: str | None = None, search: str | None = None) -> list[dict]:
    query = "SELECT * FROM products"
    conditions: list[str] = []
    params: list[object] = []

    if category:
        conditions.append("category = ?")
        params.append(category)

    if search:
        like_value = f"%{search.lower()}%"
        conditions.append("(lower(name) LIKE ? OR lower(category) LIKE ? OR lower(description) LIKE ?)")
        params.extend([like_value, like_value, like_value])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC"

    connection = get_connection()
    rows = connection.execute(query, params).fetchall()
    connection.close()
    return [row_to_product(row) for row in rows]


def get_product(product_id: int) -> dict | None:
    connection = get_connection()
    row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    connection.close()
    return row_to_product(row) if row else None


def list_categories() -> list[str]:
    connection = get_connection()
    rows = connection.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    connection.close()
    return [row["category"] for row in rows]


def create_user(full_name: str, email: str, password: str, role: str = "customer") -> dict:
    normalized_email = email.strip().lower()
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (full_name.strip(), normalized_email, hash_password(password), role, utc_now()),
            )
            row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return sanitize_user(row)
    finally:
        connection.close()


def authenticate_user(email: str, password: str) -> dict | None:
    connection = get_connection()
    row = connection.execute(
        "SELECT * FROM users WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    connection.close()
    if not row or not verify_password(password, row["password_hash"]):
        return None
    return sanitize_user(row)


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    connection = get_connection()
    with connection:
        connection.execute(
            "INSERT INTO sessions (user_id, token, created_at) VALUES (?, ?, ?)",
            (user_id, token, utc_now()),
        )
    connection.close()
    return token


def delete_session(token: str) -> None:
    connection = get_connection()
    with connection:
        connection.execute("DELETE FROM sessions WHERE token = ?", (token,))
    connection.close()


def get_user_by_token(token: str) -> dict | None:
    connection = get_connection()
    row = connection.execute(
        """
        SELECT users.id, users.full_name, users.email, users.role, users.created_at
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        ORDER BY sessions.id DESC
        LIMIT 1
        """,
        (token,),
    ).fetchone()
    connection.close()
    return dict(row) if row else None


def delete_user_account(user_id: int) -> None:
    connection = get_connection()
    with connection:
        order_ids = [row["id"] for row in connection.execute("SELECT id FROM orders WHERE user_id = ?", (user_id,)).fetchall()]
        if order_ids:
            connection.executemany("DELETE FROM order_items WHERE order_id = ?", [(order_id,) for order_id in order_ids])
        connection.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
        connection.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.close()


def create_order(
    user_id: int,
    customer_name: str,
    phone: str,
    address_line: str,
    city: str,
    payment_method: str,
    notes: str,
    items: list[dict],
    payment_status: str = "Pending",
    payment_provider: str = "",
    payment_intent_id: str = "",
) -> dict:
    if not items:
        raise ValueError("Cart is empty.")

    connection = get_connection()
    try:
        with connection:
            validated_items = []
            subtotal = 0
            for entry in items:
                product = connection.execute("SELECT * FROM products WHERE id = ?", (entry["product_id"],)).fetchone()
                if not product:
                    raise ValueError("One of the selected products no longer exists.")
                quantity = int(entry["quantity"])
                if quantity <= 0:
                    raise ValueError("Quantity must be greater than zero.")
                if product["inventory"] < quantity:
                    raise ValueError(f"{product['name']} does not have enough stock.")
                subtotal += product["price"] * quantity
                validated_items.append((product, quantity))

            shipping_fee = 0 if subtotal >= 12000 else 800
            total = subtotal + shipping_fee
            order_number = f"LYRA-{secrets.randbelow(900000) + 100000}"
            tracking_status = "Paid" if payment_status in {"succeeded", "paid", "Paid"} else "Pending"
            history = [
                {
                    "status": tracking_status,
                    "message": "Order received successfully.",
                    "timestamp": utc_now(),
                }
            ]
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    user_id, order_number, customer_name, phone, address_line, city, payment_method,
                    payment_status, payment_provider, payment_intent_id, notes, subtotal, shipping_fee,
                    total, status, tracking_number, tracking_status, tracking_history, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    order_number,
                    customer_name.strip(),
                    phone.strip(),
                    address_line.strip(),
                    city.strip(),
                    payment_method.strip(),
                    payment_status.strip() or "Pending",
                    payment_provider.strip(),
                    payment_intent_id.strip(),
                    notes.strip(),
                    subtotal,
                    shipping_fee,
                    total,
                    "Processing",
                    "",
                    tracking_status,
                    json.dumps(history),
                    utc_now(),
                ),
            )

            order_id = cursor.lastrowid
            for product, quantity in validated_items:
                connection.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, product_name, unit_price, quantity)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (order_id, product["id"], product["name"], product["price"], quantity),
                )
                connection.execute(
                    "UPDATE products SET inventory = inventory - ? WHERE id = ?",
                    (quantity, product["id"]),
                )

            order = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            return row_to_order(connection, order)
    finally:
        connection.close()


def list_orders(user_id: int | None = None) -> list[dict]:
    connection = get_connection()
    if user_id is None:
        rows = connection.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    else:
        rows = connection.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    orders = [row_to_order(connection, row) for row in rows]
    connection.close()
    return orders


def update_order_tracking(
    order_id: int,
    status: str,
    tracking_status: str,
    tracking_number: str,
    note: str,
) -> dict:
    connection = get_connection()
    try:
        with connection:
            row = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            if not row:
                raise ValueError("Order not found.")
            history = json.loads(row["tracking_history"] or "[]")
            history.append(
                {
                    "status": tracking_status,
                    "message": note.strip() or f"Order updated to {tracking_status}.",
                    "timestamp": utc_now(),
                }
            )
            connection.execute(
                """
                UPDATE orders
                SET status = ?, tracking_status = ?, tracking_number = ?, tracking_history = ?
                WHERE id = ?
                """,
                (status, tracking_status, tracking_number.strip(), json.dumps(history), order_id),
            )
            updated = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
            return row_to_order(connection, updated)
    finally:
        connection.close()


def create_product(payload: dict) -> dict:
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO products (
                    sku, name, category, description, price, compare_at_price, badge, inventory,
                    rating, display_emoji, accent_color, sizes, colors, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["sku"],
                    payload["name"],
                    payload["category"],
                    payload["description"],
                    payload["price"],
                    payload["compare_at_price"],
                    payload["badge"],
                    payload["inventory"],
                    payload["rating"],
                    payload["display_emoji"],
                    payload["accent_color"],
                    json.dumps(payload["sizes"]),
                    json.dumps(payload["colors"]),
                    payload.get("image_url", ""),
                ),
            )
            row = connection.execute("SELECT * FROM products WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return row_to_product(row)
    finally:
        connection.close()


def update_product(product_id: int, payload: dict) -> dict:
    connection = get_connection()
    try:
        with connection:
            connection.execute(
                """
                UPDATE products
                SET sku = ?, name = ?, category = ?, description = ?, price = ?, compare_at_price = ?,
                    badge = ?, inventory = ?, rating = ?, display_emoji = ?, accent_color = ?,
                    sizes = ?, colors = ?, image_url = ?
                WHERE id = ?
                """,
                (
                    payload["sku"],
                    payload["name"],
                    payload["category"],
                    payload["description"],
                    payload["price"],
                    payload["compare_at_price"],
                    payload["badge"],
                    payload["inventory"],
                    payload["rating"],
                    payload["display_emoji"],
                    payload["accent_color"],
                    json.dumps(payload["sizes"]),
                    json.dumps(payload["colors"]),
                    payload.get("image_url", ""),
                    product_id,
                ),
            )
            row = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
            if not row:
                raise ValueError("Product not found.")
            return row_to_product(row)
    finally:
        connection.close()


def delete_product(product_id: int) -> None:
    connection = get_connection()
    with connection:
        connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.close()
