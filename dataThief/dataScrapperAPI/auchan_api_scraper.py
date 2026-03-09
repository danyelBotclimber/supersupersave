import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

# Constants
PAGE_SIZE = 200 # Auchan handles larger page sizes well
BASE = "https://www.auchan.pt"
RETAILER = "Auchan"
SCRAPED_AT = datetime.utcnow().isoformat()

urls = [
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=produtos-frescos&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=biologico-e-escolhas-alimentares&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=limpeza-da-casa-e-roupa&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=auchan-pet&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=caes&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=gatos&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=papelaria-livraria&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-e-prepara%C3%A7%C3%A3o&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=fraldas-e-toalhitas&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=fraldas-e-toalhitas&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=banho-higiene-1&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=higiene-oral&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=cremes-de-corpo-e-rosto&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=papel-higi%C3%A9nico-e-len%C3%A7os-papel&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={PAGE_SIZE}" 
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html"
}

def parse_price(price_str):
    if not price_str:
        return None
    # Auchan often uses ',' for decimals in text, but provides 'content' attribute with '.'
    price_str = price_str.replace("€", "").replace(",", ".").replace("\xa0", "").strip()
    try:
        return float(price_str)
    except:
        return None

def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []

    # Auchan products are wrapped in .auc-product or directly in .product-tile
    for tile in soup.select(".auc-product"):
        product = {}
        
        # Inner product container holds the data-pid
        core_data = tile.select_one(".product-tile")
        if not core_data:
            continue

        product["retailer"] = RETAILER
        product["scraped_at"] = SCRAPED_AT
        product["id"] = core_data.get("data-pid")

        # Name
        name_element = tile.select_one(".pdp-link a")
        product["name"] = name_element.get_text(strip=True) if name_element else None

        # Price - Attempting to get from the 'content' attribute first as it's cleaner
        price_val = tile.select_one(".price .sales .value")
        if price_val and price_val.has_attr('content'):
            product["price"] = parse_price(price_val['content'])
        elif price_val:
            product["price"] = parse_price(price_val.get_text(strip=True))
        else:
            product["price"] = None

        # Price per unit (e.g., 2.4 €/Kg)
        unit_price = tile.select_one(".auc-measures--price-per-unit")
        product["price_per_unit"] = unit_price.get_text(strip=True) if unit_price else None

        # Qty - Auchan usually includes this in the name or the unit price string
        # We'll store the unit price string as the qty raw data if specific qty isn't found
        product["qty"] = {"raw": product["price_per_unit"]}

        # URL
        link = name_element.get("href") if name_element else None
        product["url"] = (BASE + link) if link and not link.startswith("http") else link

        # Image - Auchan uses lazy loading with data-src
        image = tile.select_one("img.tile-image")
        if image:
            # Try data-src first, fallback to src
            product["image"] = image.get("data-src") or image.get("src")
        else:
            product["image"] = None

        products.append(product)

    return products

all_products = []

for url in urls:
    start = 0
    
    # Extract category name for logging
    current_cat = re.search(r'cgid=([^&]+)', url).group(1)
    print(f"--- Processing Category: {current_cat} ---")

    while True:
        page_url = url.replace("start=0", f"start={start}")
        
        try:
            r = requests.get(page_url, headers=headers)
            r.raise_for_status()
            
            products = parse_products(r.text)

            if not products:
                print(f"No more products found for {current_cat}.")
                break

            all_products.extend(products)
            print(f"Fetched {len(products)} products (Total so far: {len(all_products)})")

            # Demandware pagination: increment by the size requested
            start += PAGE_SIZE
                
        except Exception as e:
            print(f"Error fetching {page_url}: {e}")
            break

print(f"\n✅ Extraction Complete. Total products collected: {len(all_products)}")

# Save to file
filename = "../../data/auchan/products.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"Saved products to {filename} ✅")