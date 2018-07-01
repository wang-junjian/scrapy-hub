# [乔丹](http://www.qiaodan.com/)
> 抓取产品对应的图片

## 创建项目
```shell
scrapy startproject qiaodan
```

## 创建采集图片的爬虫
```shell
cd qiaodan
scrapy genspider capture qiaodan.com
```

## 解析元数据
* 编辑 items.py
```py
import scrapy


class ProductItem(scrapy.Item):
    number = scrapy.Field()
    img_urls = scrapy.Field()
```

* 编辑 capture.py
```py
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
        url = response.xpath('//div[@class="product-item"]/div[@class="item-img"]/a/@href')
        url = self.home_url + url.extract()[0]
        print('>> 产品链接地址：', url)

        yield scrapy.Request(url, self.parse_product_images)

    def parse_product_images(self, response):
        product_number = response.xpath('//span[@class="qd-tt"]/text()').extract()[0]
        print('>> 产品号码：', product_number)

        urls = []
        img_urls = response.xpath('//ul[@class="imagebg"]/li/a/img/@src')
        for img_url in img_urls:
            url = self.home_url + img_url.extract()
            urls.append(url)
            print('>> 产品图片链接地址：', url)

        item = ProductItem(
            number=product_number,
            img_urls=urls
        )

        yield item
```

## 下载图片
* 移除 settings.py 中的注释
```py
ITEM_PIPELINES = {
    'qiaodan.pipelines.QiaodanPipeline': 300,
}
```

* 编辑 pipelines.py
```py
import scrapy
import os


class QiaodanPipeline(object):
    images_dir = 'images/'

    def process_item(self, item, spider):
        for (index, img_url) in enumerate(item['img_urls']):
            request = scrapy.Request(img_url)
            dfd = spider.crawler.engine.download(request, spider)
            dfd.addBoth(self.return_item, item, item['number'], index+1)

        return dfd

    def return_item(self, response, item, product_number, image_url_index):
        if response.status != 200:
            return item

        url = response.url
        basename = os.path.basename(url)
        _, ext_name = os.path.splitext(basename)

        dir = self.images_dir + product_number
        filename = '{}/{}d{}{}'.format(dir, product_number, image_url_index, ext_name)

        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(filename, "wb") as f:
            f.write(response.body)

        return item
```

3.编辑product_number.txt(根目录下)，输入要抓取的的货号，一行一个。

4.抓取图片，图片存储在根目录下的images下。
```shell
cd qiaodan
scrapy crawl capture
```