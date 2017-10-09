# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
import re
from articlespider.items import ZhihuQuestionItem, ZhihuAnswerItem
from scrapy.loader import ItemLoader
import json, datetime


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['zhihu.com']
    start_urls = ['http://zhihu.com/']
    start_answer_url = 'http://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}'

    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.zhihu.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.3637.220 Safari/537.36',
    }
    cookie = {'_zap':'20474f86-aaef-4b4a-9d0d-23d8750d4696',
                'q_c1':'7c8ba046b5b14d1fb21d88afcbe9dfb9|1506238107000|1506238107000',
                'aliyungf_tc':'AQAAACEI82+2UAIAYuHGb+14ShtlJNZg',
                'd_c0':"AACCn1rtewyPTpMWuqmTIa6NwJXVSiOZNMM=|1507255041",
                'q_c1':'5681b4aa114146f2b330d111d9b36d2c|1507261719000|1507261719000',
                'capsion_ticket':"2|1:0|10:1507262859|14:capsion_ticket|44:ZGYyYzEzMzAwOGQ4NGFlYWFmNTkxMTkzNmY3YjkwN2Y=|2e48a6c01a91b27a990bfebd8a198a99fea4081784a7842ca7361440cdee620c",
                'r_cap_id':"OTFkNjY3ZDNjYmFlNDU4M2JkYzYxZDRhMzk3M2JkNGU=|1507262878|2442ed83369f1ddade4104db2ed90c2a78ac207d",
                'cap_id':"MTUzYzRkYjNkOTMxNDUwZjlkZGZjYzVkZTE3MzhiNjE=|1507262878|dfb7f223beb5e54fe44fc91663dabc83f6fd8c61",
                'z_c0':'Mi4xdVBnZkJnQUFBQUFBQUlLZld1MTdEQmNBQUFCaEFsVk4xbzctV1FDVFpXUU9qelNmQU9Ga1Rqc0Vld09GazVOVkZn|1507262934|9e6d6f15794bbd8d7e7d8f991661680393d03541',
                's-q':'%E4%BA%BA%E5%B7%A5', 's-i':'1', 'sid':'uob74nu6', 's-t':'autocomplete',
                '__utma':'51854390.375587936.1507255046.1507255046.1507262147.2',
                '__utmb':'51854390.0.10.1507262147',
                '__utmc':'51854390',
                '__utmz':'51854390.1507262147.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/bruce-37-33/activities',
                '__utmv':'51854390.100--|2=registration_date=20171006=1^3=entry_date=20170924=1',
                '_xsrf':'b2871fa4-45f6-4517-b74e-cc7d48c6635c'}

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/', headers=self.headers,cookies=self.cookie)]

    #提取主页面信息(新的request_url及问题的id)
    def parse(self, response):
        all_urls = response.css('a::attr(href)').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith('https') else False, all_urls)  # 注意这个用法
        for url in all_urls:
            match_obj = re.match('.*zhihu.com/question/(\d+)', url)
            if match_obj:  # 如果是问答类的url则进行分析，如果不是则继续提取其中的url来分析
                request_url = match_obj.group(0)
                question_id = match_obj.group(1)
                yield scrapy.Request(request_url, meta={'zhihu_id':question_id}, headers=self.headers,cookies=self.cookie,callback=self.parse_question)
                # break
                yield scrapy.Request(request_url, headers=self.headers, cookies=self.cookie, callback=self.parse)
            else:
                # pass
                yield scrapy.Request(url,headers=self.headers, cookies=self.cookie,callback=self.parse)
    def parse_question(self, response):
        #处理'问题‘相关信息， 从页面中提取具体的question items
        #用ItemLoader有一个缺点，就是如果字段为空不会返回None，而是什么都不返回，这就造成入库的时候找不着这个字段
        #所以我们要想办法设置，如果提取不到值，就赋值一个默认值，比如这里的content
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        question_id = response.meta.get('zhihu_id')

        item_loader.add_css('answer_num', '.List-headerText span::text')
        item_loader.add_css('title', 'h1.QuestionHeader-title::text')
        item_loader.add_value('zhihu_id', question_id)
        item_loader.add_css('topics', '.QuestionHeader-topics .Popover div::text')
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('content', '//div[@class="QuestionHeader-detail"]//text()|'  # 注意这里的双斜杠//text()
                                         '//h1[@class="QuestionHeader-title"]/text()')

        item_loader.add_css('comments_num', '.QuestionHeader-Comment button::text')
        item_loader.add_css('watch_user_num', '.NumberBoard-value::text')

        question_items = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0),
                             headers=self.headers, cookies=self.cookie,
                             callback=self.parse_answer)
        yield question_items

    def parse_answer(self, response):
        items = ZhihuAnswerItem()
        text = json.loads(response.text)  # 这个函数分析的是一个json接口的url，返回的是个json

        next_url = text['paging']['next']
        is_end = text['paging']['is_end']
        for data in text['data']:
            items['zhihu_id'] = data['id']
            items['url'] = data['url']
            items['question_id'] = data['question']['id']
            items['author_id'] = data['author']['id'] if 'id' in data['author'] else None  # 注意这个用法
            items['content'] = data['content'] if 'content' in data else data['excerpt']
            items['voteup_num'] = data['voteup_count']
            items['comments_num'] = data['comment_count']
            items['create_time'] = data['created_time']
            items['update_time'] = data['updated_time']
            items['crawl_time'] = datetime.datetime.now()
            yield items  # 因为data有很多同层级字段，所以每遍历一层就返回一次，不然的话返回的就是最后一次遍历的
        if not is_end:  # 如果不是最后一页就继续分析
            yield scrapy.Request(next_url, headers=self.headers, cookies=self.cookie, callback=self.parse_answer)



