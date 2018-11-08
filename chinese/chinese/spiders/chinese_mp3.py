# -*- coding: utf-8 -*-
import scrapy
from chinese.items import ChineseItem


class ChineseMp3Spider(scrapy.Spider):
    name = "chinese"
    allowed_domains = ["baidu.com"]
    input_filename = 'words.txt'
    
    def start_requests(self):
        words = []
        with open(self.input_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                words.append(line.strip('\n'))

        if not words:
            print('文件 {} 为空'.format(self.input_filename))

        # url_f = "https://hanyu.baidu.com/s?wd={}&ptype=zici"
        url_f = "https://hanyu.baidu.com/s?wd={}&ptype=zici"

        for word in words:
            url = url_f.format(word)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        root_xpath = "//div[@id='pinyin']/"
        word_xpath = root_xpath + "h2/strong/text()"
        pinyin_xpath = root_xpath + "h2/span/b/text()"
        mp3_url_xpath = root_xpath + "h2/span/a/@url"

        word = response.xpath(word_xpath).extract()[0]
        pinyin = response.xpath(pinyin_xpath).extract()[0]
        pinyin = self.__strip_pinyin(pinyin)
        mp3_url = response.xpath(mp3_url_xpath).extract()[0]
        
        item = ChineseItem(word=word, pinyin=pinyin, mp3_url=mp3_url)

        yield item
    
    @staticmethod
    def __strip_pinyin(pinyin):
        return pinyin.strip('[] ')