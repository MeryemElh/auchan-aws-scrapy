import scrapy


class AuchanSpider(scrapy.Spider):
    name = 'auchan'
    allowed_domains = ['auchan.fr']
    start_urls = ['http://auchan.fr/']

    def parse(self, response):
        pass
