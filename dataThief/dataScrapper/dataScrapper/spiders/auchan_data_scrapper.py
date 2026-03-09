# scrapy crawl auchanData -O ../../../data/auchan/data_test.json 

import scrapy
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

SZ = 200

class AuchanDataExtractor(scrapy.Spider):
    name = "auchanData"
    
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
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=produtos-frescos&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=biologico-e-escolhas-alimentares&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=limpeza-da-casa-e-roupa&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=auchan-pet&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=caes&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=gatos&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=papelaria-livraria&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=alimentacao-e-prepara%C3%A7%C3%A3o&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=fraldas-e-toalhitas&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=fraldas-e-toalhitas&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=banho-higiene-1&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=higiene-oral&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=cremes-de-corpo-e-rosto&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}",
        f"https://www.auchan.pt/on/demandware.store/Sites-AuchanPT-Site/pt_PT/Search-UpdateGrid?cgid=papel-higi%C3%A9nico-e-len%C3%A7os-papel&prefn1=soldInStores&prefv1=000&srule=price-low-to-high&start=0&sz={SZ}"
    ]

    def parse(self, response):
        products = response.xpath("//div[contains(@class, 'auc-product-tile')]")
        
        if not products:
            self.logger.info("No more products found.")
            return

        for product in products:
            gtm_raw = product.xpath("./@data-gtm").get()
            if gtm_raw:
                try:
                    # 1. Base Info from GTM JSON
                    item = json.loads(gtm_raw)
                    item['retailer'] = "Auchan"
                    
                    # --- PRICE CONVERSION ---
                    # Convert "price" string to float if it exists
                    if 'price' in item and item['price']:
                        try:
                            item['price'] = float(item['price'])
                        except ValueError:
                            item['price'] = None # Or keep as string if preferred
                    
                    # 2. Enhanced Quantity Extraction
                    item['qty_min'] = product.xpath("normalize-space(.//span[@class='auc-measures--avg-weight']/text())").get()
                    
                    # 3. Price per unit extraction & conversion
                    ppu_raw = product.xpath("normalize-space(.//span[@class='auc-measures--price-per-unit']/text())").get()
                    item['price_per_unit_label'] = ppu_raw # The full string "0.48 €/un"
                    
                    # Optional: Extract just the number from "0.48 €/un"
                    if ppu_raw:
                        try:
                            # Grabs the first part before the space and replaces comma with dot
                            ppu_num = ppu_raw.split(' ')[0].replace(',', '.')
                            item['price_per_unit'] = float(ppu_num)
                        except (ValueError, IndexError):
                            item['price_per_unit'] = None

                    # 4. Pricing & Promotions
                    item['is_promo'] = product.xpath(".//div[contains(@class, 'auc-price__promotion')]").get() is not None
                    
                    # 5. URLs & Images
                    rel_url = product.xpath(".//a[contains(@class, 'link')]/@href").get()
                    item['url'] = response.urljoin(rel_url) if rel_url else ""
                    
                    image_url = product.xpath(".//picture/source[1]/@data-srcset").get()
                    if not image_url:
                        image_url = product.xpath(".//img/@data-src").get()
                    item['image_url'] = image_url.split('?')[0] if image_url else ""

                    # 6. Labels
                    item['labels'] = product.xpath(".//img[@class='auc-product-labels__icon']/@alt").getall()

                    yield item
                except json.JSONDecodeError:
                    continue

        # --- Pagination Logic ---
        parsed_url = urlparse(response.url)
        params = parse_qs(parsed_url.query)
        current_start = int(params.get('start', [0])[0])
        next_start = current_start + SZ
        
        params['start'] = [str(next_start)]
        next_url = urlunparse(parsed_url._replace(query=urlencode(params, doseq=True)))
        
        yield scrapy.Request(url=next_url, callback=self.parse)