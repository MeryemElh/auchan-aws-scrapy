from scrapy import Spider, Request, Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http.response.html import HtmlResponse
from scrapy.exceptions import IgnoreRequest
from twisted.python.failure import Failure

from aws_auchan_crawler.items import AwsAuchanCrawlerItem
from aws_auchan_crawler.utils.regex_parser import RegexParser


class AuchanSpider(Spider):
    name = 'auchan'
    allowed_domains = ['auchan.fr']
    start_urls = ['http://www.auchan.fr/']
    category_extractor = LinkExtractor(restrict_css=".navigation-node")
    sub_category_extractor = LinkExtractor(restrict_xpaths="//*[text() = 'Voir tous les produits']")
    product_extractor = LinkExtractor(restrict_xpaths="//article")
    regex_parser = RegexParser()

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
        #TODO: not necessarily multiple pages
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
        #TODO: scrap the prices and other data if useful
        # Gets the part of the website that contains the product data
        # It's necessary to isolate it as if not, it will also get the data of recommended products
        product = AwsAuchanCrawlerItem()

        product_detail_selector = response.css(".product__top")[0]
        with open("test2.html", "w+", encoding="utf-8") as f:
            f.write(f"{response.url}\n\n{product_detail_selector.get()}")

        # The categories are hierarchical with the first one always being "Accueil" and the last one being the product name
        categories = response.xpath("//span[contains(@class, 'site-breadcrumb__item')]//meta[@itemprop = 'name']/@content").getall()
        brand = response.xpath("//span[contains(@class, 'site-breadcrumb__item')]//meta[@itemprop = 'brand']/@content").get()

        # None if the rating isn't found, else it's an int represented as a string
        rating_people_count = product_detail_selector.css(".rating-value__value::text").get()
        rating_value = response.css(".reviews__statistics .rating-value--big::text").get()

        # Use regexes to parse the data, known formats for now are 'Contenance : 300g' and 'Lot de 6 pièces'
        additional_attributes = self.regex_parser.parse_additional_info(product_detail_selector.css(".product-attribute::attr(aria-label)").getall())

        price_container = product_detail_selector.css(".product-price__container")

        available = None
        if product_detail_selector.css(".product-unavailable__message").get():
            available = False

        if price_container:
            available = True

            price_container = price_container[0]
        
            price = price_container.xpath("//meta[@itemprop = 'price']/@content").get()            
            currency = price_container.xpath("//meta[@itemprop = 'priceCurrency']/@content").get()

            base_price_container = price_container.css(".product-price--small::text").get()
            if base_price_container:
                base_price_container = base_price_container.split("/")
                base_price = {
                    "value": base_price_container[0].strip().replace(",", ".", 1),
                    "unit": base_price_container[1].strip()
                }
                while base_price["value"][-1] > "9" or base_price["value"][-1] < "0":
                    base_price["value"] = base_price["value"][:len(base_price["value"])-1]
            else:
                base_price = None
        
        else:
            price = None
            currency = None
            base_price = None
        
        product['name'] = categories[-1]
        product['url'] = response.url
        product['categories'] = categories
        product['brand'] = brand
        product['rating_people_count'] = rating_people_count
        product['rating_value'] = rating_value
        product['additional_attributes'] = additional_attributes
        product['base_price'] = base_price
        product['price'] = price
        product['currency'] = currency
        product['availability'] = available
        return product