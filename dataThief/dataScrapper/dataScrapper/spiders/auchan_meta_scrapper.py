# scrapy crawl auchanMeta -O spiders/auchan_metadata.json

import scrapy
import re

class AuchanMetaSpider(scrapy.Spider):
    name = "auchanMeta"
    
    start_urls = [
        "https://www.auchan.pt/pt/produtos-frescos/",
        "https://www.auchan.pt/pt/alimentacao/",
        "https://www.auchan.pt/pt/bebidas-e-garrafeira/",
        "https://www.auchan.pt/pt/biologicos-e-alternativas/",
        "https://www.auchan.pt/pt/limpeza-e-cuidados-do-lar/",
        "https://www.auchan.pt/pt/beleza-e-higiene/higiene-oral/",
        "https://www.auchan.pt/pt/beleza-e-higiene/cuidados-solares/",
        "https://www.auchan.pt/pt/beleza-e-higiene/amaciadores-e-mascaras-de-cabelo/",
        "https://www.auchan.pt/pt/beleza-e-higiene/champo-e-coloracao/",
        "https://www.auchan.pt/pt/beleza-e-higiene/cremes-de-corpo-e-rosto/",
        "https://www.auchan.pt/pt/beleza-e-higiene/produtos-para-cabelo/",
        "https://www.auchan.pt/pt/beleza-e-higiene/cuidados-de-saude/",
    ]

    def parse(self, response):
        # 1. Get the Title
        title = response.xpath("//h1[contains(@class, 'auc-category-title')]/text()").get()
        title = title.strip() if title else "Unknown"

        # 2. Get the results text (e.g., "1.0 - 48 de 3388 resultados")
        results_text = response.xpath("//div[contains(@class, 'auc-js-search-results-count')]/text()").get()
        
        total_products = 0
        products_per_page = 24 # Default fallback

        if results_text:
            # CLEANING: Remove dots so "1.0" becomes "10" and doesn't break the regex
            # and "3.388" (if they use thousands separators) becomes "3388"
            clean_text = results_text.replace('.', '').replace(',', '')

            # REGEX: Find the number before 'de' and the number after 'de'
            # (\d+) matches the digits
            match = re.search(r'(\d+)\s+de\s+(\d+)', clean_text)
            
            if match:
                products_per_page = int(match.group(1)) # This captures the 48
                total_products = int(match.group(2))    # This captures the 3388
        
        yield {
            "name": title,
            "url": response.url,
            "totalProducts": total_products,
            "productsPerPage": products_per_page
        }