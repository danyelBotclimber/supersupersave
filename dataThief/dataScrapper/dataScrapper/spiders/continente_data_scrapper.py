# scrapy crawl continenteData -O ../../../data/continente/data_test.json 

import scrapy
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime

SZ = 200

class ContinenteDataExtractor(scrapy.Spider):
    name = "continenteData"
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0...',
        'CONCURRENT_REQUESTS': 32,      # Increase this (default is 16)
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'DOWNLOAD_DELAY': 0.5,          # Reduce or remove if the site allows
        'COOKIES_ENABLED': False,       # Disabling cookies speeds up requests
        'RETRY_TIMES': 2,               # Fewer retries for speed
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    start_urls = [
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=frescos&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=laticinios&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=congelados&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=mercearias&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=bebidas&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=biologicos&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=limpeza&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=bebe-ver-todos&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=higiene-beleza&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=animais&pmin=0%2e01&start=0&sz={SZ}",
        f"https://www.continente.pt/on/demandware.store/Sites-continente-Site/default/Search-UpdateGrid?cgid=papelaria-material&pmin=0%2e01&start=0&sz={SZ}"
    ]

    def parse(self, response):
        products = response.xpath("//div[contains(@class, 'product-tile') and @data-product-tile-impression]")
        
        if not products:
            return

        for product in products:
            json_raw = product.xpath("./@data-product-tile-impression").get()
            if json_raw:
                try:
                    raw = json.loads(json_raw)
                    
                    # --- ROBUST IMAGE EXTRACTION ---
                    # 1. Try lazy-load attribute
                    image_url = product.xpath(".//img[contains(@class, 'ct-tile-image')]/@data-src").get()
                    
                    # 2. Try standard src attribute
                    if not image_url:
                        image_url = product.xpath(".//img[contains(@class, 'ct-tile-image')]/@src").get()
                    
                    # 3. Try fallback to parent's confirmation JSON (very common in Continente)
                    if not image_url:
                        conf_image_raw = product.xpath("./parent::div/@data-confirmation-image").get()
                        if conf_image_raw:
                            try:
                                image_url = json.loads(conf_image_raw).get('url')
                            except:
                                pass
                    
                    # Clean the URL (remove resizing query parameters)
                    final_image = image_url.split('?')[0] if image_url else ""

                    # --- STANDARDIZED OBJECT ---
                    item = {
                        "retailer": "Continente",
                        "id": raw.get('id'),
                        "product_name": raw.get('name'),
                        "price": float(raw.get('price', 0)),
                        "url": response.urljoin(product.xpath(".//a[contains(@class, 'image-link')]/@href").get()),
                        "image_url": final_image,
                        "qty": product.xpath("normalize-space(.//p[contains(@class, 'pwc-tile--quantity')]/text())").get(),
                        # Keep secondary price for reference if needed
                        "secondary_price": product.xpath("normalize-space(.//div[contains(@class, 'pwc-tile--price-secondary')]/text())").get(),
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    yield item
                except Exception as e:
                    self.logger.error(f"Error parsing product: {e}")
                    continue

        # --- Pagination ---
        parsed_url = urlparse(response.url)
        params = parse_qs(parsed_url.query)
        current_start = int(params.get('start', [0])[0])
        next_start = current_start + SZ
        
        params['start'] = [str(next_start)]
        next_url = urlunparse(parsed_url._replace(query=urlencode(params, doseq=True)))
        
        yield scrapy.Request(url=next_url, callback=self.parse)