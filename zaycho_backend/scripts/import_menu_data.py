import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_MENU_FILE = BASE_DIR / "menu_data.txt"
ASSETS_ROOT = BASE_DIR / "assets" / "images"
OUTPUT_FILE = BASE_DIR / "data" / "menu_items.json"

ITEM_PATTERN = re.compile(
    r"(?ms)-\s*category\s*[:.]?\s*(?P<category>.*?)\s*\n"
    r"\s*-\s*product name\s*[:.]?\s*(?P<name>.*?)\s*\n"
    r"\s*-\s*price\s*[:.]?\s*[¥Y]?(?P<price>\d+)\s*\n"
    r"\s*-\s*image_url\s*[:.]?\s*(?P<image>.*?)\s*\n"
    r"\s*-\s*description\s*[:.]?\s*(?P<description>.*?)(?=\n[—\-]{10,}|\n\s*[⚫️①②③④⑤⑥⑦⑧⑨⑩]|\Z)"
)

IMAGE_OVERRIDES = {
    "tea_eaves_Assorted/0007.png": "tea_eaves_Assorted/0007 2.png",
    "canned_foods/0024.png": "canned_foods/0024 2.png",
    "canned_foods/0025.png": "canned_foods/IMG_9426.jpg.webp",
    "pickles_leaves/0036.png": "salads/0036.jpg",
    "pickles_leaves/0037.png": "salads/0037.jpg",
    "crackers_dried/0038.png": "crackers_dried/MinLan-Fish-Cracker.jpg.webp",
    "crackers_dried/0039.png": "crackers_dried/690d3bdde4e0885a024c05a497765def.png.webp",
    "Soup/0040png": "Soup/0040.png",
    "pickles_leaves/0044.png": "vegetarian/0044.png",
    "pickles_leaves/0045.png": "vegetarian/0045.png",
    "pickles_leaves/0046.png": "asian_groceries/0046.png",
    "pickles_leaves/0047.png": "asian_groceries/0047.png",
}


def clean_text(value):
    replacements = {
        "\xa0": " ",
        "\u200b": "",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\x1f": "\n",
        "\x1d": "\n",
        "\r": "",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value


def normalize_field(value):
    value = clean_text(value).replace('"', "").strip()
    return " ".join(value.split())


def available_assets():
    return {str(path.relative_to(ASSETS_ROOT)) for path in ASSETS_ROOT.rglob("*") if path.is_file()}


def resolve_image_path(raw_path, known_assets):
    raw_path = normalize_field(raw_path)
    marker = "assets/images/"
    if marker in raw_path:
        raw_path = raw_path.split(marker, 1)[1]

    raw_path = raw_path.lstrip("/")
    raw_path = IMAGE_OVERRIDES.get(raw_path, raw_path)

    if raw_path in known_assets:
        return f"/assets/images/{raw_path}"

    match = re.search(r"(\d{4})", raw_path)
    if match:
        digits = match.group(1)
        candidates = [asset for asset in known_assets if digits in asset]
        if len(candidates) == 1:
            return f"/assets/images/{candidates[0]}"

    raise ValueError(f"Missing asset for menu item image: {raw_path}")


def parse_menu_items():
    raw_text = clean_text(RAW_MENU_FILE.read_text(encoding="utf-8", errors="replace"))
    known_assets = available_assets()
    menu_items = []
    seen = set()

    for match in ITEM_PATTERN.finditer(raw_text):
        item = {
            "category": normalize_field(match.group("category")),
            "name": normalize_field(match.group("name")),
            "price": int(match.group("price")),
            "image_url": resolve_image_path(match.group("image"), known_assets),
            "description": normalize_field(match.group("description")),
        }

        dedupe_key = (
            item["category"],
            item["name"],
            item["price"],
            item["image_url"],
            item["description"],
        )
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        menu_items.append(item)

    for index, item in enumerate(menu_items, start=1):
        item["id"] = index

    return menu_items


def main():
    menu_items = parse_menu_items()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(menu_items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(menu_items)} menu items to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
