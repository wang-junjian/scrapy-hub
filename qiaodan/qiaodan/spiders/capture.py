# -*- coding: utf-8 -*-
import scrapy
from qiaodan.items import ProductItem


class CaptureSpider(scrapy.Spider):
    name = 'capture'
    allowed_domains = ['qiaodan.com']
    home_url = 'http://www.qiaodan.com'
    search_url = 'http://www.qiaodan.com/chanpin/suosuo.php?keyword={}'
    input_filename = 'product_number.txt'

    def start_requests(self):
        product_numbers = []
        with open(self.input_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                product_numbers.append(line.strip('\n'))

        print(product_numbers)
        if not product_numbers:
            print('文件 {} 为空'.format(self.input_filename))

        for product_number in product_numbers:
            url = self.search_url.format(product_number)
            yield scrapy.Request(url, self.parse_product_link)

    def parse_product_link(self, response):
        if response.status == 200:
            url = response.xpath('//div[@class="product-item"]/div[@class="item-img"]/a/@href').extract()

            if url:
                url = self.home_url + url[0]
                print('>> 产品链接地址：', url)

                yield scrapy.Request(url, self.parse_product_images)
            else:
                print('>> 产品号码不存在')

    def parse_product_images(self, response):
        if response.status == 200:
            product_number = response.xpath('//span[@class="qd-tt"]/text()').extract()
            if product_number:
                product_number = product_number[0]
                print('>> 产品号码：', product_number)

                urls = []
                img_urls = response.xpath('//ul[@class="imagebg"]/li/a/img/@src')
                for img_url in img_urls:
                    url = self.home_url + img_url.extract()
                    urls.append(url)
                    print('>> 产品图片链接地址：', url)

                if img_urls:
                    item = ProductItem(
                        number=product_number,
                        img_urls=urls
                    )

                    yield item
