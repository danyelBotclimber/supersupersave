# scrapy crawl pingoDoceData -O ../../../data/pingodoce/data_test.json 

import scrapy
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime

SZ = 200

class PingoDoceDataExtractor(scrapy.Spider):
    name = "pingoDoceData"
    
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

    # You can move these to a JSON file later like we did with Auchan/Continente
    start_urls = [
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_frutasevegetais_100&pmin=0%2e04&start=0&sz={SZ}"
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_talho_200&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_peixaria_300&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_padariaepastelaria_400&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_charcutariaqueijos_500&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_ovos_600&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_manteigamargarinanatas_700&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_iogurtessobremesas_800&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_leitebebidasvegetais_900&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_congelados_1000&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_cafechaachocolatados_1100&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_bolachascereaisguloseimas_1200&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_mercearia_1300&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_aguassumosrefrigerantes_1400&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_cervejassidras_1500&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_espirituosas_1600&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_vinhos_1700&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_limpeza_1800&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_casaeletrodomesticos_1900&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_higienepessoalbeleza_2100&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_bebecrianca_2200&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_animais_2300&pmin=0%2e04&start=0&sz={SZ}",
        f"https://www.pingodoce.pt/on/demandware.store/Sites-pingo-doce-Site/default/Search-UpdateGrid?cgid=ec_alternativasalimentares_2400&pmin=0%2e04&start=0&sz={SZ}"
    ]

    def parse(self, response):
        products = response.xpath("//div[contains(@class, 'product-tile-pd')]")
        if not products: return

        for product in products:
            gtm_raw = product.xpath("./@data-gtm-info").get()
            image_url = product.xpath(".//img[contains(@class, 'product-tile-component-image')]/@src").get()

            if gtm_raw:
                try:
                    gtm_data = json.loads(gtm_raw)
                    if gtm_data.get('items'):
                        raw = gtm_data['items'][0]
                        
                        # Standardized Object
                        item = {
                            "retailer": "Pingo Doce",
                            "id": raw.get('item_id'),
                            "product_name": raw.get('item_name'),
                            "price": float(raw.get('price', 0)),
                            "url": response.urljoin(product.xpath(".//a[contains(@class, 'product-tile-image-link')]/@href").get()),
                            "image_url": image_url, # Extracted from HTML
                            "qty": product.xpath("normalize-space(.//div[contains(@class, 'product-unit')]/text())").get(),
                            "display_price": " ".join(product.xpath(".//span[contains(@class, 'sales')]//text()").getall()).strip(),
                            "scraped_at": datetime.now().isoformat()
                        }
                        yield item
                except:
                    continue

        # --- Pagination Logic ---
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        
        # Get current 'start' and 'sz' values
        current_start = int(query_params.get('start', [0])[0])
        sz = int(query_params.get('sz', [SZ])[0])
        
        # Increment start by sz
        next_start = current_start + sz
        
        # Update parameters and build next URL
        query_params['start'] = [str(next_start)]
        new_query = urlencode(query_params, doseq=True)
        next_url = urlunparse(parsed_url._replace(query=new_query))
        
        yield scrapy.Request(url=next_url, callback=self.parse)