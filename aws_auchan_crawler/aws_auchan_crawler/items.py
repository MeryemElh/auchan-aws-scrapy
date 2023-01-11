import scrapy


class AwsAuchanCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    categories = scrapy.Field()
    rating_people_count = scrapy.Field()
    rating_value = scrapy.Field()
    additional_attributes = scrapy.Field()
    base_price = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    img = scrapy.Field()
    brand = scrapy.Field()
    availability = scrapy.Field()
    variants = scrapy.Field()
