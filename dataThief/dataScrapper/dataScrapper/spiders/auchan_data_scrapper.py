# scrapy crawl auchanData -O ../../../data/auchan/data_test.json 

import scrapy
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime

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
        if not products: return

        for product in products:
            gtm_raw = product.xpath("./@data-gtm").get()
            if gtm_raw:
                try:
                    raw = json.loads(gtm_raw)
                    image_raw = product.xpath(".//picture/source[1]/@data-srcset").get() or product.xpath(".//img/@data-src").get()
                    
                    # Standardized Object
                    item = {
                        "retailer": "Auchan",
                        "id": raw.get('id'),
                        "product_name": raw.get('name'),
                        "price": float(raw.get('price', 0)) if raw.get('price') else 0.0,
                        "url": response.urljoin(product.xpath(".//a[contains(@class, 'link')]/@href").get()),
                        "image_url": image_raw.split('?')[0] if image_raw else "",
                        "qty": product.xpath("normalize-space(.//span[@class='auc-measures--avg-weight']/text())").get(),
                        "price_per_unit": product.xpath("normalize-space(.//span[@class='auc-measures--price-per-unit']/text())").get(),
                        "is_promo": product.xpath(".//div[contains(@class, 'auc-price__promotion')]").get() is not None,
                        "scraped_at": datetime.now().isoformat()
                    }
                    yield item
                except:
                    continue

        # --- Pagination Logic ---
        parsed_url = urlparse(response.url)
        params = parse_qs(parsed_url.query)
        current_start = int(params.get('start', [0])[0])
        next_start = current_start + SZ
        
        params['start'] = [str(next_start)]
        next_url = urlunparse(parsed_url._replace(query=urlencode(params, doseq=True)))
        
        yield scrapy.Request(url=next_url, callback=self.parse)