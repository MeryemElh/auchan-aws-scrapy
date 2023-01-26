import json
import boto3

from itemadapter import ItemAdapter

class AwsAuchanCrawlerFilePipeline:

    def open_spider(self, spider):
        self.file = open('products.json', 'w+')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item

class AwsAuchanCrawlerS3Pipeline:

    def open_spider(self, spider):
        self.s3_client = boto3.client('s3')

    def process_item(self, item, spider):

        self.s3_client.upload_file(item['img']['path'], "auchan-web-crawler", item['s3_paths']["image_path"])

        self.s3_client.put_object(
            Body=json.dumps(ItemAdapter(item).asdict()),
            Bucket='auchan-web-crawler',
            Key=item['s3_paths']['item_path']
        )

        return item
