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

## 解析元数据代码
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
```

* xpath语法
    *  `//div[@class="product-item"]/div[@class="item-img"]/a/@href`
    
    ```html
    <div class="product-list-ret-item">
        <div class="product-item">
            <div class="item-img">
                <a href="/chanpin/lanqiu/clothing/2018-03-28/24230.html"><img src="/d/file/chanpin/lanqiu/clothing/2018-03-28/18e504c84409bb41d4eff66a79d216e6.png"></a>
                <!--<div class="new-products-top"></div>--><!--新品推荐才有-->
                <!--<div class="new-products-bot"></div>--><!--新品推荐才有-->
                <a href="/chanpin/lanqiu/clothing/2018-03-28/24230.html" class="more"></a>
                <a href="/chanpin/lanqiu/clothing/2018-03-28/24230.html" class="good"><i>0</i></a>
            </div>
            <div class="item-fot">
                <p>篮球套</p>
                <div class="num"><span>ANT2382101</span></div>
                <div class="price"><i>¥</i><span>159</span></div>
            </div>
        </div>
    </div>
    ```

    * `//ul[@class="imagebg"]/li/a/img/@src`
    
    ```html
    <ul class="imagebg" id="imagebg"> 
        <li data-sPic=/d/file/chanpin/lanqiu/clothing/2018-03-28/800e92ee5a4234a5826613b5349f378f.png><a href="javascript:;" class="bannerbg_main" ><img src=/d/file/chanpin/lanqiu/clothing/2018-03-28/800e92ee5a4234a5826613b5349f378f.png alt=></a></li>&nbsp;<li data-sPic=/d/file/chanpin/lanqiu/clothing/2018-03-28/b4db752b497eb5990523a74195b1e5ee.png><a href="javascript:;" class="bannerbg_main" ><img src=/d/file/chanpin/lanqiu/clothing/2018-03-28/b4db752b497eb5990523a74195b1e5ee.png alt=></a></li>&nbsp;<li data-sPic=/d/file/chanpin/lanqiu/clothing/2018-03-28/b8a24318d0b1ed82512e471e551c6009.png><a href="javascript:;" class="bannerbg_main" ><img src=/d/file/chanpin/lanqiu/clothing/2018-03-28/b8a24318d0b1ed82512e471e551c6009.png alt=></a></li>&nbsp;<li data-sPic=/d/file/chanpin/lanqiu/clothing/2018-03-28/1c4a4e1eaef8f45c8c5ef6685ca6daf6.png><a href="javascript:;" class="bannerbg_main" ><img src=/d/file/chanpin/lanqiu/clothing/2018-03-28/1c4a4e1eaef8f45c8c5ef6685ca6daf6.png alt=></a></li>&nbsp;<li data-sPic=/d/file/chanpin/lanqiu/clothing/2018-03-28/04cb96f40506d00fe605220c96ef801b.png><a href="javascript:;" class="bannerbg_main" ><img src=/d/file/chanpin/lanqiu/clothing/2018-03-28/04cb96f40506d00fe605220c96ef801b.png alt=></a></li>
    </ul>
    ```

    * `//span[@class="qd-tt"]/text()`

    ```html
    <span class="qd-tt">ANT2382101</span>
    ```

## 下载图片代码
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
```

> item['img_urls']、item['number'] 不能使用. item.img_urls、item.number

## 运行爬虫采集图片
* 编辑 product_number.txt，输入要抓取的的货号，一行一个。
* 抓取图片，图片存储在根目录下的images。
```shell
scrapy crawl capture
```

## 参考资料
* [Scrapy简单入门及实例讲解](https://www.cnblogs.com/kongzhagen/p/6549053.html)
* [Scrapy爬虫入门教程九 Item Pipeline](https://www.jianshu.com/p/8d65da080c47)

