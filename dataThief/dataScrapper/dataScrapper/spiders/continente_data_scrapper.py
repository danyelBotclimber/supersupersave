# scrapy crawl continenteData -O ../../../data/continente/data_test.json 

import scrapy
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

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
            self.logger.info("End of results reached.")
            return

        for product in products:
            json_raw = product.xpath("./@data-product-tile-impression").get()
            if json_raw:
                try:
                    item = json.loads(json_raw)
                    item['retailer'] = "Continente"
                    
                    # 1. Image Extraction
                    # Primary: The lazy-loaded high-res image
                    image_url = product.xpath(".//img[contains(@class, 'ct-tile-image')]/@data-src").get()
                    
                    # Fallback: Extract from data-confirmation-image JSON attribute if img tag fails
                    if not image_url:
                        conf_image_raw = product.xpath("./parent::div/@data-confirmation-image").get()
                        if conf_image_raw:
                            try:
                                conf_data = json.loads(conf_image_raw)
                                image_url = conf_data.get('url')
                            except:
                                pass
                    
                    # Clean the image URL (remove query params for full size)
                    item['image_url'] = image_url.split('?')[0] if image_url else ""
                    
                    # 2. Quantity & Description
                    item['quantity_label'] = product.xpath("normalize-space(.//p[contains(@class, 'pwc-tile--quantity')]/text())").get()
                    
                    # 3. Pricing
                    price_parts = product.xpath(".//span[contains(@class, 'pwc-tile--price-primary')]//text()").getall()
                    item['display_price'] = "".join(price_parts).strip() if price_parts else f"{item.get('price')}€"
                    
                    # Secondary price (e.g., "1,48€/un")
                    item['secondary_price'] = product.xpath("normalize-space(.//div[contains(@class, 'pwc-tile--price-secondary')]/text())").get()

                    # 4. Product URL
                    rel_url = product.xpath(".//a[contains(@class, 'image-link')]/@href").get()
                    item['url'] = response.urljoin(rel_url) if rel_url else ""

                    yield item
                except json.JSONDecodeError:
                    continue

        # --- Pagination ---
        parsed_url = urlparse(response.url)
        params = parse_qs(parsed_url.query)
        current_start = int(params.get('start', [0])[0])
        next_start = current_start + SZ
        
        params['start'] = [str(next_start)]
        next_url = urlunparse(parsed_url._replace(query=urlencode(params, doseq=True)))
        
        yield scrapy.Request(url=next_url, callback=self.parse)