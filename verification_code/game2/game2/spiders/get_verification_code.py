# -*- coding: utf-8 -*-
import scrapy
import os
from datetime import datetime


class GetVerificationCodeSpider(scrapy.Spider):
    name = 'get_verification_code'
    allowed_domains = ['game2.cn']
    start_urls = ['http://game2.cn/']
    verification_code_url = 'http://www.game2.cn/verifyCode.php'
    images_dir = 'images/'
    download_times = 100

    def start_requests(self):
        for _ in range(self.download_times):
            yield scrapy.Request(self.verification_code_url, dont_filter=True)

    def parse(self, response):
        # if response.status == 200:

        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        image_filename = self.get_image_filename()
        with open(image_filename, "wb") as f:
            f.write(response.body)

    def get_image_filename(self):
        name = str(int(datetime.now().timestamp()*1000000))
        filename = '{}/{}{}'.format(self.images_dir, name, '.png')
        return filename
