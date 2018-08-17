# 采集game2验证码

## 不过滤重复的URL，修改文件get_verification_code.py
```py
def start_requests(self):
    for _ in range(self.download_times):
        yield scrapy.Request(self.verification_code_url, dont_filter=True)
```

## 设置下载间隔时间为1秒，修改文件settings.py
```
DOWNLOAD_DELAY = 1
```
