import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
import re

PAGE_SIZE = 35

BASE = "https://www.continente.pt"
RETAILER = "Continente"
SCRAPED_AT = datetime.now(timezone.utc).isoformat()

urls = [
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=frescos&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=laticinios&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=congelados&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=mercearias&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=bebidas&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=biologicos&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=limpeza&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=bebe-ver-todos&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=higiene-beleza&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=animais&pmin=0%2e01&start=0&sz={PAGE_SIZE}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=papelaria-material&pmin=0%2e01&start=0&sz={PAGE_SIZE}"
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}


def parse_price(price_str):
    if not price_str:
        return None
    price_str = price_str.replace("€", "").replace(",", ".").strip()
    try:
        return float(price_str)
    except:
        return None


def parse_qty(qty_text):
    if not qty_text:
        return None

    # Example: "Quant. Mínima = 2 un"
    match = re.search(r'(\d+)\s*([a-zA-Z]+)', qty_text)
    if match:
        return {
            "value": int(match.group(1)),
            "unit": match.group(2)
        }

    return {"raw": qty_text}


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for tile in soup.select(".productTile"):

        product = {}

        product["retailer"] = RETAILER
        product["scraped_at"] = SCRAPED_AT

        product["id"] = tile.select_one(".product")["data-pid"]

        name = tile.select_one(".pwc-tile--description")
        product["name"] = name.get_text(strip=True) if name else None

        price = tile.select_one(".pwc-tile--price-primary")
        price_text = price.get_text(strip=True) if price else None
        product["price"] = parse_price(price_text)

        price_kg = tile.select_one(".pwc-tile--price-secondary")
        product["price_per_unit"] = price_kg.get_text(strip=True) if price_kg else None

        qty = tile.select_one(".pwc-tile--quantity")
        product["qty"] = parse_qty(qty.get_text(strip=True)) if qty else None

        link = tile.select_one(".ct-pdp-link a")
        product["url"] = BASE + link["href"] if link else None

        image = tile.select_one("img.ct-tile-image")
        product["image"] = image["data-src"] if image else None

        products.append(product)

    return products


all_products = []

for url in urls:

    start = 0
    page_size = PAGE_SIZE

    while True:

        page_url = url.replace("start=0", f"start={start}")
        print(page_url)

        r = requests.get(page_url, headers=headers)

        products = parse_products(r.text)

        if not products:
            break

        all_products.extend(products)

        print(f"Fetched {len(products)} products (start={start})")

        start += page_size


print(f"\nTotal products collected: {len(all_products)}")

with open("data/continente/products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print("Saved products to products.json ✅")