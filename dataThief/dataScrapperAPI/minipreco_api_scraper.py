import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone
import re
import time
import random

# Modern UTC timestamp
MAX_PAGE = 5
SCRAPED_AT = datetime.now(timezone.utc).isoformat()
RETAILER = "Minipreço"
BASE = "https://www.minipreco.pt"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.minipreco.pt/",
        "Connection": "keep-alive"
    }

def parse_price(price_str):
    if not price_str: return None
    # Convert "0,44 €" to 0.44
    price_str = price_str.replace("€", "").replace(",", ".").strip()
    try:
        return float(price_str)
    except:
        return None

def parse_products_from_soup(soup):
    products_list = []
    items = soup.select(".product-list__item")
    
    for item in items:
        grid = item.select_one(".prod_grid")
        if not grid: continue
        
        product = {
            "retailer": RETAILER,
            "scraped_at": SCRAPED_AT,
            "id": grid.get("data-productcode"),
            "name": item.select_one(".details").get_text(strip=True) if item.select_one(".details") else None,
        }

        price_el = item.select_one(".price")
        product["price"] = parse_price(price_el.get_text(strip=True)) if price_el else None

        price_kg = item.select_one(".pricePerKilogram")
        product["price_per_unit"] = price_kg.get_text(strip=True) if price_kg else None

        link = item.select_one("a.productMainLink")
        product["url"] = BASE + link["href"] if link else None

        image = item.select_one("img.lazy")
        product["image"] = (image.get("data-original") or image.get("src")) if image else None

        products_list.append(product)
    return products_list

all_products = []
urls = [
    f"https://www.minipreco.pt/produtos/c/WEB.000.000.00000?q=%3Aname-asc&page=0&disp=",
]

for base_url in urls:
    current_page = 0  # Starting from the first page
    
    print(f"\n--- Starting Category: {base_url} ---")

    while True:
        # Construct the URL for the current page
        current_url = re.sub(r'page=\d+', f'page={current_page}', base_url)
        print(f"🔍 Fetching Page {current_page} | URL: {current_url}")

        try:
            r = requests.get(current_url, headers=get_headers(), timeout=15)
            
            if r.status_code == 429:
                print("🚨 429 Blocked! Waiting 60s...")
                time.sleep(60)
                continue 

            if r.status_code != 200:
                print(f"❌ Status {r.status_code} received. Stopping category.")
                break

            soup = BeautifulSoup(r.text, "html.parser")
            page_products = parse_products_from_soup(soup)
            
            # --- BREAK CONDITION ---
            if not page_products or (MAX_PAGE != 0 and current_page == MAX_PAGE):
                print(f"🏁 No products found on page {current_page} or limit of max pages reached! Category finished.")
                break

            all_products.extend(page_products)
            print(f"✅ Page {current_page}: Found {len(page_products)} items. (Total so far: {len(all_products)})")

            # Increment and wait
            current_page += 1
            time.sleep(random.uniform(3, 5))

        except Exception as e:
            print(f"❌ Error during request: {e}")
            break

# Save results
print(f"\n✨ Scrape complete. Total items collected: {len(all_products)}")
with open("data/minipreco/products.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"Saved to minipreco_products.json ✅")