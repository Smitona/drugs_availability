# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DrugItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    drug_name = scrapy.Field()
    type_of_privilege = scrapy.Field()
    drug_form = scrapy.Field()
    quantity = scrapy.Field()


async def write_item_in_DB(self, response, drug_form_number):
        """Добавить в базу данных"""

        item = DrugItem()
        item['drug_name'] =
        item['type_of_privilege'] = 
        item['drug_form'] = 
        item['quantity'] =
        yield item