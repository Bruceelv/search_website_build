# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from ..items import JobboleArticleItem, ArticleItemLoader
from ..utils.common import get_md5
import datetime
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        art_urls = response.css('.grid-8 .floated-thumb .post-thumb a')
        for art_url in art_urls:
            front_img_url = art_url.css('img::attr(src)').extract_first()
            art_url = art_url.css('::attr(href)').extract_first()
            yield Request(parse.urljoin(response.url,art_url),meta={'front_img_url':front_img_url},callback=self.parse_details)  # 这里一定要加self哦

        #css选择器，一个标签如果有两个class属性，可以连着写div.navigation.margin-20
        next_url = response.css('#archive > div.navigation.margin-20 > a.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(next_url,callback=self.parse)


    def parse_details(self,response):
        # items = JobboleArticleItem()
        # title = response.css('.entry-header h1::text').extract_first()
        # # 使用extract_first()而不是使用extract()[0]的好处是，就算列表为空，用前者取值的时候也不会报错，用后者则会报错
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().replace('·',
        #                                                                                                        '').strip()
        # zan = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first()
        # store = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first()[:-2].strip()
        # comments = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()[:-2].strip()
        # contents = response.xpath('//div[@class="entry"]')[0].xpath('string()').extract_first() \
        #     .replace('\n', '').replace('\t', '').replace('\r', '')  # 注意这个用法哦
        # tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags = ','.join(tag_list)  # 注意这个用法，Python里的语法

        '''
        #通过css选择器进行选择
        #class属性为entry-meta-hide-on-mobile的p标签里的内容

        create_date = response.css('p.entry-meta-hide-on-mobile::text').extract_first().replace('·', '').strip()
        try:
            create_date = datetime.datetime.strptime(create_date,'%Y/%m/%d').date()
        except:
            create_date = datetime.datetime.now()
        zan = response.css('.vote-post-up h10::text').extract_first(0)
        if not zan:
            zan = 0
        store = response.css('span.bookmark-btn::text').extract_first()[:-2].strip()
        if not store:
            store = 0
        comments = response.css('a[href="#article-comment"] span::text').extract_first()[:-2].strip()
        if not comments:
            comments = 0
        contents = response.css('div.entry').extract_first()
        tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)
        front_img_url = response.meta.get('front_img_url','')  # 用get方法而不是直接用字典取值是为了防止数据为空的时候抛异常
        url = response.url
        url_md5 = get_md5(url)
        for field in items.fields:
            try:
                if field == 'front_img_url':
                    items[field] = [front_img_url]  # 保存图片的时候需要列表格式
                else:
                    items[field] = eval(field)
            except NameError:
                self.logger.debug('Field is not define.' + field)
        '''



        item_loader = ArticleItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css('title', '.entry-header h1::text')
        item_loader.add_css('create_date', 'p.entry-meta-hide-on-mobile::text')
        item_loader.add_css('zan', '.vote-post-up h10::text')
        item_loader.add_css('store', 'span.bookmark-btn::text')
        item_loader.add_css('comments', 'a[href="#article-comment"] span::text')
        item_loader.add_css('tags', 'p.entry-meta-hide-on-mobile a::text')
        item_loader.add_value('front_img_url', [response.meta.get('front_img_url','')])
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_md5',get_md5(response.url))
        item_loader.add_css('contents', 'div.entry')

        items = item_loader.load_item()
        yield items
