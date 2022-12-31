from scrapy import Spider, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse


class AuchanSpider(Spider):
    name = 'auchan'
    allowed_domains = ['auchan.fr']
    start_urls = ['http://www.auchan.fr/']
    category_extractor = LinkExtractor(restrict_css=".navigation-node")

    def parse(self, response: HtmlResponse):
        for link in self.category_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse_category)

    def parse_category(self, response: HtmlResponse):
        #TODO: Parse sub-categories
        with open("text.txt", "a+", encoding="utf-8") as f:
            f.write(f"{response.url}\n")