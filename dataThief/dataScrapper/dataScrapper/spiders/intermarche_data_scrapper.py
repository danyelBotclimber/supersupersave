# scrapy crawl intermarcheData -O ../../../data/intermarche/data_test.json 

import scrapy
import os
import re
from datetime import datetime

class IntermarcheLocalExtractor(scrapy.Spider):
    name = "intermarcheData"
    
    # Path to your Tampermonkey downloads
    html_folder = '../../../html_dumps/intermarche/'

    def start_requests(self):
        if not os.path.exists(self.html_folder):
            self.logger.error(f"Directory not found: {self.html_folder}")
            return

        for filename in os.listdir(self.html_folder):
            if filename.endswith(".html"):
                file_path = f"file://{os.path.abspath(os.path.join(self.html_folder, filename))}"
                yield scrapy.Request(url=file_path, callback=self.parse)

    def parse(self, response):
        base_domain = "https://www.intermarche.pt"

        products = response.xpath("//div[contains(@class, 'product') and contains(@class, 'productList__orderItem')]")
        current_time = datetime.now().isoformat()

        for product in products:
            # 1. Price Logic (Handling data-price or visual span)
            raw_price = product.xpath("./@data-price").get()
            if not raw_price or raw_price == "0":
                visual_price = product.xpath("string(.//span[contains(@class, 'product__productPrice')])").get()
                if visual_price:
                    # Cleans "1,00 €" -> "1.00"
                    raw_price = re.sub(r'[^\d,.]', '', visual_price).replace(',', '.')

            # 2. Price Per Unit (e.g., "3,99 €/Kg")
            # We grab the text inside product__prices that isn't the main price span
            ppu_text = product.xpath("string(.//div[contains(@class, 'product__prices')])").get()
            ppu_match = re.search(r'(\d+,\d+\s*€/(?:Kg|L|un|dose))', ppu_text) if ppu_text else None
            price_per_unit = ppu_match.group(1).replace(',', '.') if ppu_match else None

            # 3. Brand and Name
            brand = product.xpath("string(.//span[contains(@class, 'product__brand')])").get()
            if brand:
                brand = brand.strip().rstrip('-').strip()
            
            # 4. Quantity Info (e.g., "1 un = 250 gr (aprox.)")
            qty_info = product.xpath("string(.//div[contains(@class, 'product__texts')])").get()
            # Clean up the string to find the quantity line
            qty_match = re.search(r'(\d+\s*(?:un|gr|kg|ml|L|dose).*?\(aprox\.\)|\d+\s*(?:gr|kg|ml|L))', qty_info, re.IGNORECASE)
            quantity = qty_match.group(1).strip() if qty_match else None

            # 5. Promotion & Offer Expiry
            promo_text = product.xpath(".//span[contains(@class, 'highlightTag__tip')]/text()").getall()
            promo_msg = " ".join(promo_text).replace('\n', ' ').strip() if promo_text else None
            
            # Extract date from "Oferta válida... até 12/03/2026"
            expiry_date = None
            if promo_msg:
                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', promo_msg)
                expiry_date = date_match.group(1) if date_match else None
            
            relative_url = product.xpath(".//a[contains(@class, 'product__info')]/@href").get()
            product_url = f"{base_domain}{relative_url}" if relative_url else None

            yield {
                "retailer": "Intermarché",
                "id": product.xpath("./@data-id").get(),
                "ean": product.xpath("./@id").get().replace('productEan_', '') if product.xpath("./@id").get() else None,
                "brand": brand,
                "product_name": product.xpath("./@data-name").get(),
                "price": float(raw_price) if raw_price else 0.0,
                "price_per_unit": price_per_unit,
                "qty": quantity,
                "is_promo": "hasPromo" in (product.xpath(".//span[contains(@class, 'product__productPrice')]/@class").get() or ""),
                "promo_info": promo_msg,
                "offer_expires": expiry_date,
                "origin": product.xpath("string(.//div[contains(@class, 'product__highlight')])").get(),
                "image_url": product.xpath(".//img[contains(@class, 'product__image')]/@src").get(),
                "product_url": product_url,
                "scraped_at": current_time,
                "source_file": response.url.split('/')[-1]
            }