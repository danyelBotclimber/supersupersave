# scrapy crawl auchanData -O ../../../data/auchan/data_test.json 

import scrapy
import json
import os

class AuchanDataExtractor(scrapy.Spider):
    name = "auchanData_backup"
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'CONCURRENT_REQUESTS': 2,
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def __init__(self, *args, **kwargs):
        super(AuchanDataExtractor, self).__init__(*args, **kwargs)
        
        # Load the categories from your generated JSON file
        # Make sure the path matches where you saved the helper script output
        metadata_file = 'spiders/auchan_metadata.json'
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.categories = json.load(f)
            self.logger.info(f"Successfully loaded {len(self.categories)} categories from {metadata_file}")
        else:
            self.categories = []
            self.logger.error(f"CRITICAL: {metadata_file} not found!")

    def start_requests(self):
        for cat in self.categories:
            # Check if we have valid data before requesting
            if not cat.get('url'):
                continue

            # Auchan uses 'start' for offset and 'sz' for page size
            first_url = f"{cat['url']}?start=0&sz={cat.get('productsPerPage', 24)}"
            
            yield scrapy.Request(
                url=first_url,
                callback=self.parse,
                meta={
                    'cat_config': cat,
                    'current_start': 0
                }
            )

    def parse(self, response):
        cat_config = response.meta['cat_config']
        current_start = response.meta['current_start']
        
        self.logger.info(f"Processing {cat_config['name']} | Start: {current_start}")

        products = response.xpath("//div[contains(@class, 'product-tile') and @data-gtm]")

        for product in products:
            json_data = product.xpath("./@data-gtm").get()
            
            if json_data:
                try:
                    item = json.loads(json_data)
                    item['scraped_category'] = cat_config['name']
                    
                    # Quantity/Measure
                    measure = product.xpath(".//span[contains(@class, 'auc-measures--price-per-unit')]/text()").get()
                    item['measure_price'] = measure.strip() if measure else ""
                    
                    # Display Price
                    display_price = product.xpath(".//span[contains(@class, 'sales')]//span[@class='value']/text()").get()
                    if display_price:
                        item['display_price'] = display_price.strip() + " €"
                    else:
                        item['display_price'] = f"{item.get('price')} €"

                    # Product URL
                    relative_url = product.xpath(".//a[contains(@class, 'link')]/@href").get()
                    item['url'] = response.urljoin(relative_url) if relative_url else ""

                    yield item

                except json.JSONDecodeError:
                    continue

        # --- Pagination Logic ---
        # We use the totalProducts we found in the metadata script
        next_start = current_start + cat_config.get('productsPerPage', 24)

        if next_start < cat_config.get('totalProducts', 0):
            next_url = f"{cat_config['url']}?start={next_start}&sz={cat_config['productsPerPage']}"
            
            yield response.follow(
                next_url,
                callback=self.parse,
                meta={
                    'cat_config': cat_config,
                    'current_start': next_start
                }
            )