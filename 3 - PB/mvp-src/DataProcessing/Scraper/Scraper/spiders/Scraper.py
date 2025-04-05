import scrapy

class VimarScraper(scrapy.Spider):
    name = 'Scraper'
    start_urls = [f"https://www.vimar.com/it/it/catalog/product/index/liv/A0L102?page={i}" for i in range(1, 7)] + [f"https://www.vimar.com/it/it/catalog/product/index/liv/B0L110?page={i}" for i in range(1, 24)]

    def parse(self, response):
        products = response.css('div.col-2.col-xl-1.d-none.d-sm-block')
        for product in products:
            product_id = product.css('strong.text-break::text').get()
            if product_id:
                product_url = f"https://www.vimar.com/it/it/catalog/product/index/code/{product_id}"
                yield response.follow(product_url, self.parse_product, meta={'id': product_id})

    def parse_product(self, response):
        product_id = response.meta['id']
        second_paragraph = response.css('div.col-12.col-lg.py-2 p:nth-of-type(2)')
        title = second_paragraph.css('strong::text').get()
        description = second_paragraph.xpath('./br/following-sibling::text()').get()

        if description:
            description = description.strip()

        third_paragraph = response.css('div.col-12.col-lg.py-2 p:nth-of-type(3)')
        price = third_paragraph.xpath('./br/following-sibling::text()').get()

        documentation_div = response.css('div.col-12.col-lg-6')
        links = documentation_div.css('a::attr(href)').getall()

        technical_data = {}
        details = response.css('div.row.align-items-center > div')
        for detail in details:
            key = detail.css('strong::text').get()
            value = detail.xpath('./br/following-sibling::text()').get()
            if key and value:
                technical_data[key.strip()] = value.strip()
        
        images = response.css('div.card.justify-content-center.p-4.pb-5.text-center.border-0 > a::attr(href)').getall()

        yield {
            'id': product_id,
            'title': title,
            'description': description,
            'price': price,
            'technical_data': technical_data,
            'images': images,
            'documentation': links,
        }