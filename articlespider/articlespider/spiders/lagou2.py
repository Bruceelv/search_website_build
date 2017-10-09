# -*- coding: utf-8 -*-
import scrapy
from items import LagouJobItem, LagouItemLoader
from utils.common import get_md5
import datetime, re, time

#scrapy spider爬取拉钩
class Lagou2Spider(scrapy.Spider):
    name = 'lagou2'
    allowed_domains = ['lagou.com']
    start_urls = ['https://www.lagou.com/zhaopin/ceshi/']

    def parse(self, response):
        #提取所有类型的招聘主页
        urls = response.css('a::attr(href)').extract()
        for url in urls:
            pattern = re.compile('.*zhaopin/.*')
            if pattern.match(url):
                yield scrapy.Request(url, callback=self.parse_index)


    def parse_index(self, response):
        #提取各招聘主页的具体职位招聘
        urls = response.css('a::attr(href)').extract()
        for url in urls:
            pattern = re.compile('.*jobs/\d+.html')
            if pattern.match(url):
                yield scrapy.Request(url, callback=self.parse_detail,)
                print(url)
                # time.sleep(5)
        pass

    def parse_detail(self, response):
        #分析具体职位的详细信息
        item_loader = LagouItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css('title', '.job-name .name::text')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_md5', get_md5(response.url))
        item_loader.add_css('salary', '.job_request .salary::text')
        item_loader.add_xpath('job_city', '//dd[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('work_years', '//dd[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//dd[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//dd[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('publish_time', '.publish_time::text')
        item_loader.add_css('job_advantage', '.job-advantage p::text')
        item_loader.add_css('job_desc', '.job_bt div')
        # job_desc = response.css('.job_bt')[0].xpath('string()').extract_first()  # 不用ItemLoader可以这么写
        item_loader.add_css('job_addr', '.work_addr')
        item_loader.add_css('company_name', '.job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '.job_company dt a::attr(href)')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_value('crawl_time', datetime.datetime.now())

        job_item = item_loader.load_item()
        print(job_item.keys())
        print(response.headers)
        if 'title' in job_item.keys():
            return job_item

        # return job_item