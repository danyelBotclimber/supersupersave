# scrapy crawl continenteMeta -O spiders/continente_metadata.json
import scrapy

class ContinenteMetaSpider(scrapy.Spider):
    name = "continenteMeta"
    
    # Input list with your specific parameters
    start_urls = [
        "https://www.continente.pt/frescos/?start=0&srule=FRESH-Generico&pmin=0.01",
        "https://www.continente.pt/laticinios-e-ovos/?start=0&srule=FOOD-Laticinios&pmin=0.01",
        "https://www.continente.pt/congelados/?start=0&srule=FOOD-Congelados&pmin=0.01",
        "https://www.continente.pt/mercearia/?start=0&srule=FOOD-Mercearia&pmin=0.01",
        "https://www.continente.pt/bebidas-e-garrafeira/?start=0&srule=FOOD-Bebidas&pmin=0.01",
        "https://www.continente.pt/bio-e-saudavel/?start=0&srule=FOOD-BIO&pmin=0.01",
        "https://www.continente.pt/limpeza/?start=0&srule=FMCG-LL&pmin=0.01",
        "https://www.continente.pt/bebe/ver-todos/?start=0&srule=Trading-categorias-destaques&pmin=0.01",
        "https://www.continente.pt/beleza-e-higiene/?start=0&srule=FOOD-HB-Perfumes&pmin=0.01",
        "https://www.continente.pt/animais/?start=0&srule=FOOD-Planning&pmin=0.01",
        "https://www.continente.pt/papelaria/?start=0&srule=Continente&pmin=0.01"
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'LOG_LEVEL': 'INFO'
    }

    def parse(self, response):
        # 1. Extract the Title from the new H1 location
        # This targets the text "Frescos" inside the h1 tag
        name = response.css('h1.pwc-h3::text').get()
        if name:
            name = name.strip()
        else:
            # Fallback to the data-title attribute if the text node is empty
            name = response.css('h1.pwc-h3::attr(data-title)').get()
            if name:
                name = name.split('|')[0].strip()

        # 2. Extract Metadata from the grid-footer
        grid_footer = response.css('div.grid-footer')
        
        # total-count (e.g., 3268)
        total_products = int(grid_footer.attrib.get('data-total-count', 0))
        
        # page-size (e.g., 36.0 -> 36)
        products_per_page = int(float(grid_footer.attrib.get('data-page-size', 36)))

        # 3. Output the object
        yield {
            "name": name,
            "url": response.url, # Returns the full URL with parameters
            "totalProducts": total_products,
            "productsPerPage": products_per_page
        }