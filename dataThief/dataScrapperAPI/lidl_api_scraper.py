import requests
import json
from datetime import datetime, timezone
import re
import time
import random

# --- CONFIGURATION ---
BASE = "https://www.lidl.pt"
RETAILER = "Lidl"
SCRAPED_AT = datetime.now(timezone.utc).isoformat()
FETCH_SIZE = 48  # The batch size you identified

# Base API URL without the offset and fetchsize (we'll add those dynamically)
API_BASE_URL = "https://www.lidl.pt/q/api/search?locale=pt_PT&assortment=PT&version=2.1.0"

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'Cookie': 'LidlID=78ddf654-f4b3-44b8-8270-cea1f0fd400d; OptanonAlertBoxClosed=2026-03-07T00:12:32.605Z; utm_source=referrer_google; _gcl_au=1.1.1584406787.1772842353; adSessionId=3406654C-B25C-4D55-9C02-C928A3616B03; _ga=GA1.1.822132141.1772842353; FPID=FPID2.2.Efn7N5%2FRoEUJZwwqbGhXfKDZD%2B9hxnxRK2C8S7AywCE%3D.1772842353; i18n_redirected=pt_PT; zn=PT1; stgcct=1772844061596; wh=92; FPLC=C%2Bvg0iQ6tavNDq2Pzdx%2FfnP2IqXCcGw89pApd%2BfsVM8RoQ%2FIhX7aiWxf%2FV1XJOJ0ggmGQsoDPiMvzz5JFtJAU1NozU6B%2Fu4XMgMZ4uRNsHlTqNkXEwKebx10VVBW5g%3D%3D; UserVisits=current_visit_date:09.03.2026|last_visit_date:09.03.2026; ar=ar%3D92%3BEntityID%3D432%3Bzip%3D4810-553%3Bcity%3DGuimar%C3%A3es%3Bstreet%3DRua%20da%20Arcela; st=432; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Mar+09+2026+18%3A27%3A41+GMT%2B0000+(Western+European+Standard+Time)&version=202601.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=4c0676bc-ac02-472e-91c3-4fe01c405f29&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&crTime=1772842352853&geolocation=PT%3B03&AwaitingReconsent=false; _ga_S9KRZMHDHH=GS2.1.s1773080570$o2$g1$t1773081018$j60$l0$h234160447; FPGSID=1.1773080570.1773081019.G-S9KRZMHDHH.gwMwhX-0h9Us7uwZ9_tj9A'
}

def parse_qty_info(qty_str):
    if not qty_str: return None
    match = re.search(r'(\d+[\.,]?\d*)\s*([a-zA-Z]+)', qty_str)
    if match:
        return {"value": float(match.group(1).replace(',', '.')), "unit": match.group(2)}
    return {"raw": qty_str}

def process_items(items):
    page_data = []
    for item in items:
        if item.get("type") != "product": continue
        data_block = item.get("gridbox", {}).get("data", {})
        if not data_block: continue

        product = {
            "retailer": RETAILER,
            "scraped_at": SCRAPED_AT,
            "id": str(data_block.get("productId")),
            "name": data_block.get("fullTitle"),
            "url": BASE + data_block.get("canonicalUrl") if data_block.get("canonicalUrl") else None,
            "image": data_block.get("image")
        }

        lidl_plus = data_block.get("lidlPlus", [])
        if lidl_plus:
            p_info = lidl_plus[0].get("price", {})
            product["price"] = p_info.get("price")
            product["price_per_unit"] = p_info.get("basePrice", {}).get("text")
            product["qty"] = parse_qty_info(p_info.get("packaging", {}).get("text"))
        else:
            p_info = data_block.get("price", {})
            product["price"] = p_info.get("price")
            product["price_per_unit"] = None
            product["qty"] = None
        
        page_data.append(product)
    return page_data

# --- PAGINATION LOOP ---

all_products = []
offset = 0

print(f"📡 Starting Lidl Pagination Scrape (Batch size: {FETCH_SIZE})...")

while True:
    current_url = f"{API_BASE_URL}&offset={offset}&fetchsize={FETCH_SIZE}"
    print(f"🔍 Fetching offset {offset}...")

    try:
        response = requests.get(current_url, headers=HEADERS, timeout=30)
        
        if response.status_code == 429:
            print("🚨 429 Blocked! Waiting 60s...")
            time.sleep(60)
            continue
            
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])
        if not items:
            print("🏁 No more items found. Ending scrape.")
            break
            
        new_products = process_items(items)
        if not new_products:
            print("🏁 Items received were not products. Ending scrape.")
            break
            
        all_products.extend(new_products)
        print(f"✅ Offset {offset}: Added {len(new_products)} products. (Total: {len(all_products)})")

        # Move to the next batch
        offset += FETCH_SIZE
        
        # Be nice to the server
        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print(f"❌ Error at offset {offset}: {e}")
        break

# --- SAVE DATA ---
output_filename = "data/lidl/products.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)

print(f"\n✨ Done! Saved {len(all_products)} products to {output_filename}")