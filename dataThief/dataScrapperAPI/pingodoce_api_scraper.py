import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# Constants
PAGE_SIZE = 200
BASE = "https://www.pingodoce.pt"
RETAILER = "Pingo Doce"
SCRAPED_AT = datetime.utcnow().isoformat()

urls = [
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_frutasevegetais_100&pmin=0%2e04&start=0&sz={PAGE_SIZE}"
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_talho_200&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_peixaria_300&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_padariaepastelaria_400&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_charcutariaqueijos_500&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_ovos_600&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_manteigamargarinanatas_700&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_iogurtessobremesas_800&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_leitebebidasvegetais_900&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_congelados_1000&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_cafechaachocolatados_1100&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_bolachascereaisguloseimas_1200&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_mercearia_1300&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_aguassumosrefrigerantes_1400&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_cervejassidras_1500&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_espirituosas_1600&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_vinhos_1700&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_limpeza_1800&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_casaeletrodomesticos_1900&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_higienepessoalbeleza_2100&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_bebecrianca_2200&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_animais_2300&pmin=0%2e04&start=0&sz={PAGE_SIZE}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_alternativasalimentares_2400&pmin=0%2e04&start=0&sz={PAGE_SIZE}"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html"
}

def parse_price(price_str):
    if not price_str:
        return None
    # Clean string: remove currency, fix decimals, remove non-breaking spaces
    price_str = price_str.replace("€/Kg", "").replace("€", "").replace(",", ".").strip()
    try:
        return float(price_str)
    except:
        return None

def parse_qty(qty_text):
    if not qty_text:
        return None
    # Matches patterns like "0.21 Kg" or "500 g"
    match = re.search(r'([\d\.]+)\s*([a-zA-Z]+)', qty_text.replace(',', '.'))
    if match:
        return {
            "value": float(match.group(1)),
            "unit": match.group(2)
        }
    return {"raw": qty_text}

def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Pingo Doce products are in .product containers
    for tile in soup.select(".product"):
        product = {}
        
        # Main data container
        core_data = tile.select_one(".product-tile-pd")
        if not core_data:
            continue

        product["retailer"] = RETAILER
        product["scraped_at"] = SCRAPED_AT
        product["id"] = core_data.get("data-pid")

        # Name
        name_element = tile.select_one(".product-name-link a")
        product["name"] = name_element.get_text(strip=True) if name_element else None

        # Brand
        brand = tile.select_one(".product-brand-name")
        product["brand"] = brand.get_text(strip=True) if brand else None

        # Price - Pingo Doce often has the clean price in the 'content' attribute
        price_val = tile.select_one(".product-price .sales .value")
        if price_val and price_val.has_attr('content'):
            product["price"] = parse_price(price_val['content'])
        else:
            # Fallback to text parsing
            sales_text = tile.select_one(".product-price .sales")
            product["price"] = parse_price(sales_text.get_text(strip=True)) if sales_text else None

        # Price Per Unit/Measure
        unit_price = tile.select_one(".product-price .sales")
        product["price_per_unit"] = unit_price.get_text(strip=True) if unit_price else None

        # Quantity/Package size
        qty_element = tile.select_one(".product-unit")
        product["qty"] = parse_qty(qty_element.get_text(strip=True)) if qty_element else None

        # URL
        link = name_element.get("href") if name_element else None
        product["url"] = (BASE + link) if link and not link.startswith("http") else link

        # Image
        image = tile.select_one("img.product-tile-component-image")
        product["image"] = image.get("src") if image else None

        products.append(product)

    return products

all_products = []

for url in urls:
    start = 200
    # Try to find category name in URL for logging
    cat_match = re.search(r'cgid=([^&]+)', url)
    current_cat = cat_match.group(1) if cat_match else "unknown"
    
    print(f"--- Scraping Pingo Doce: {current_cat} ---")

    while True:
        page_url = url.replace("start=0", f"start={start}")
        print(f"Fetching: {page_url}")

        try:
            r = requests.get(page_url, headers=headers)
            r.raise_for_status()
            
            products = parse_products(r.text)

            if not products:
                print(f"Finished category {current_cat}.")
                break

            all_products.extend(products)
            print(f"Added {len(products)} products. Total: {len(all_products)}")

            start += PAGE_SIZE
            
            # Prevent infinite loops
            if start > 4000: break
                
        except Exception as e:
            print(f"Error on {page_url}: {e}")
            break

# Final Output
print(f"\n✅ Done! Total products collected: {len(all_products)}")

with open("../../data/pingodoce/products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print("Saved to pingodoce_products.json")