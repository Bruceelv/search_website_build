# -*- coding: utf-8 -*-

# Scrapy settings for articlespider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os, sys

BOT_NAME = 'articlespider'

SPIDER_MODULES = ['articlespider.spiders']
NEWSPIDER_MODULE = 'articlespider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'articlespider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
# 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
# 'Cookie':'user_trace_token=20170926225231-68f7b85e-e008-482d-a9d2-7312bbcc12a6; LGUID=20170926225232-5365345e-a2ca-11e7-aeb8-525400f775ce; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAFCAAEG19999B232EBA55774C53E0DC8084126F; _gat=1; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2Farmkaifa%2F; SEARCH_ID=81467e4792f247afab8439de2a3b2724; _gid=GA1.2.1158060426.1507366310; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1506437552,1506439068,1507366310,1507387026; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1507387056; _ga=GA1.2.1448198829.1506437552; LGSID=20171007223702-fb5eff15-ab6c-11e7-bf31-525400f775ce; LGRID=20171007223732-0d5e0a2a-ab6d-11e7-bf31-525400f775ce',
# 'Host':'www.lagou.com',
# 'Upgrade-Insecure-Requests':1
# }
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36'
user_agent_list = []
# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'articlespider.middlewares.ArticlespiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'articlespider.middlewares.RandomUserAgentMiddlware': 543,
   # 'articlespider.middlewares.RandomProxyIPMiddleware': 542,
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'articlespider.pipelines.JsonWithEncodingPipeline': 300,
   #  # 'scrapy.pipelines.images.ImagesPipeline':299,
   #  'articlespider.pipelines.ArticleImagePipeline': 288,
   # 'articlespider.pipelines.MysqlTwistedPipeline': 288,
   'articlespider.pipelines.ElasticsearchPipelines': 288,

}
IMAGES_URLS_FIELD = 'front_img_url'  # 把front_img_url这个图片链接字段的值进行保存
IMAGES_STORE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'imgs')

sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'search_website_build'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'

SQL_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SQL_DATE_FORMAT = '%Y-%m-%d'
