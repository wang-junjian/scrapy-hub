# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import os


class QiaodanPipeline(object):
    images_dir = 'images/'

    def process_item(self, item, spider):
        product_number = item['number']
        dir = self.images_dir + product_number
        if os.path.exists(dir):
            return '产品 {} 图片已经下载'.format(product_number)

        for (index, img_url) in enumerate(item['img_urls']):
            request = scrapy.Request(img_url)
            dfd = spider.crawler.engine.download(request, spider)
            dfd.addBoth(self.return_item, item, product_number, index+1)

        return dfd

    def return_item(self, response, item, product_number, image_url_index):
        if response.status != 200:
            return item

        url = response.url
        basename = os.path.basename(url)
        _, ext_name = os.path.splitext(basename)

        dir = self.images_dir + product_number
        filename = '{}/{}{}'.format(dir, image_url_index, ext_name)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(filename, "wb") as f:
            f.write(response.body)

        return item
