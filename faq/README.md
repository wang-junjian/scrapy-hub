# Scrapy FAQ

1. 读取 settings.py 中配置的变量

```py
from scrapy.utils.project import get_project_settings


class CaptureSpider(scrapy.Spider):

    def start_requests(self):
        search_url = get_project_settings().get('SEARCH_URL')
```
* [How to access scrapy settings from item Pipeline](https://stackoverflow.com/questions/14075941/how-to-access-scrapy-settings-from-item-pipeline)
