# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import os
import logging


class ChinesePipeline(object):
    mp3_dir = 'mp3/'

    def process_item(self, item, spider):
        logging.info(item)

        mp3_url = item['mp3_url']
        if not os.path.exists(self.mp3_dir):
            os.makedirs(self.mp3_dir)

        mp3_file = self.__get_pinyin_mp3_path(item['pinyin'])
        if os.path.exists(mp3_file):
            logging.info('downloaded mp3: ' + mp3_file)
            return item

        logging.info('downloading mp3: ' + mp3_url)
        request = scrapy.Request(mp3_url)
        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)

        return dfd


    def return_item(self, response, item):
        if response.status != 200:
            return item

        mp3_file = self.__get_pinyin_mp3_path(item['pinyin'])
        with open(mp3_file, "wb") as f:
            f.write(response.body)

        logging.info('save mp3: ' + mp3_file)

        return item


    def __get_pinyin_mp3_path(self, pinyin):
        return self.mp3_dir + pinyin + '.mp3'