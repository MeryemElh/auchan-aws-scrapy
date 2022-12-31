from scrapy import Spider, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from twisted.python.failure import Failure
from twisted.internet.error import AlreadyCalled


class AuchanSpider(Spider):
    name = 'auchan'
    allowed_domains = ['auchan.fr']
    start_urls = ['http://www.auchan.fr/']
    category_extractor = LinkExtractor(restrict_css=".navigation-node")

    def parse(self, response: HtmlResponse):
        for link in self.category_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse_category, errback=self.parse_category_err)

    def parse_category(self, response: HtmlResponse):
        #TODO: Parse sub-categories
        with open("text.txt", "a+", encoding="utf-8") as f:
            f.write(f"{response.url}\n")

    def parse_category_err(self, failure: Failure):
        if failure.check(IgnoreRequest):
            #TODO: log or handle the fact that auchan blocked the scraper
            pass