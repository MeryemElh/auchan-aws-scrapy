from scrapy import Spider, Request, Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from twisted.python.failure import Failure


class AuchanSpider(Spider):
    name = 'auchan'
    allowed_domains = ['auchan.fr']
    start_urls = ['http://www.auchan.fr/']
    category_extractor = LinkExtractor(restrict_css=".navigation-node")
    sub_category_extractor = LinkExtractor(restrict_xpaths="//*[text() = 'Voir tous les produits']")
    product_extractor = LinkExtractor(restrict_xpaths="//article")

    def parse(self, response: HtmlResponse):
        for link in self.category_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse_category, errback=self.parse_category_err)

    def parse_category(self, response: HtmlResponse):
        for link in self.sub_category_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse_sub_category, errback=self.parse_sub_category_err)

    def parse_category_err(self, failure: Failure):
        if failure.check(IgnoreRequest):
            #TODO: log or handle the fact that auchan blocked the scraper
            pass

    def parse_sub_category(self, response: HtmlResponse):
        list_pages =  response.css(".pagination-item::text").getall()
        last_page_nb = int(list_pages[-1])

        # Don't need to re-parse the first page a it was parsed just now
        # We will simply call the parse products function at the end using this response

        for page_nb in range(2, last_page_nb + 1):
            page_url = f"{response.url}?page={page_nb}"
            yield Request(page_url, callback=self.parse_product_page)

        # Scraping the first page products
        self.parse_product_page(response)

    def parse_sub_category_err(self, failure: Failure):
        if failure.check(IgnoreRequest):
            #TODO: log or handle the fact that auchan blocked the scraper for the sub-cat
            pass

    def parse_product_page(self, response: HtmlResponse):
        for link in self.product_extractor.extract_links(response):
            yield Request(link.url, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):
        #TODO: scrap all the product infos
        with open("text_prod_list.txt", "a+", encoding="utf-8") as f:
            f.write(f"- {response.url}\n")