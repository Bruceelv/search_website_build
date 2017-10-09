# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import datetime
from utils.common import extract_num
from settings import SQL_DATETIME_FORMAT
from w3lib.html import remove_tags
from models.es_types import ArticleType
import re

from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticleType._doc_type.using)  # 创建链接

def date_convert(value):
    create_date = value.replace('·', '').strip()
    try:
        create_date = datetime.datetime.strptime(value, '%Y/%m/%d').date()
    except:
        create_date = datetime.datetime.now()
    return create_date


def get_num(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def remove_comments_tag(value):
    if '评论' in value:
        return ''
    else:
        return value

def return_value(value):
    return value

def gen_suggests(index, info_tuple):
    #根据字符串生成搜索建议数组
    used_words = set()  #已经存在关键字，set去重
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer='ik_max_word',params={'filter':['lowercase']},body=text)
            analyzed_words = set([word['token'] for word in words['tokens'] if len(word['token']) > 1])  # 放置关键字
            new_words = analyzed_words - used_words  # 过滤掉已经存在的关键字
        else:
            new_words = set()
        if new_words:
            suggests.append({'input':list(new_words), 'weight':weight})
    return suggests

class ArticleItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()


class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
    )
    zan = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    store = scrapy.Field(
        input_processor = MapCompose(get_num)
    )
    comments = scrapy.Field(
        input_processor=MapCompose(get_num)
    )
    contents = scrapy.Field()
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comments_tag),
        output_processor = Join(',')
    )
    front_img_url = scrapy.Field(
        output_processor=MapCompose(return_value)  # 这里是output，是为了覆盖自定义的ArticleItemLoader
    )
    front_img_path = scrapy.Field()  # 图片保存路径
    url = scrapy.Field()
    url_md5 = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                    insert into jobbole_article(title, url_md5, create_date, zan)
                    VALUES (%s, %s, %s, %s)
                '''
        params = (self['title'], self['url_md5'], self['create_date'], self['zan'])
        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.content = remove_tags(self["contents"])
        article.front_img_url = self["front_img_url"]
        if "front_img_path" in self:
            article.front_img_path = self["front_img_path"]
        article.store = self["store"]
        article.zan = self["zan"]
        article.comments = self["comments"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.url_md5= self["url_md5"]

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10), (article.tags, 7)))

        article.save()
        return


class ZhihuQuestionItem(scrapy.Item):
    #知乎的问题相关的item
    zhihu_id = scrapy.Field()  # question_id
    topics = scrapy.Field()  # 话题标签
    url = scrapy.Field()  # 当前问题的url
    title = scrapy.Field()  # 问题的标题
    content = scrapy.Field()  # 问题的内容
    answer_num = scrapy.Field()  # 回答数
    comments_num = scrapy.Field()  # 评论数
    follower_num = scrapy.Field()  # 关注数量
    watch_user_num = scrapy.Field()  # 被浏览数
    crawl_time = scrapy.Field()  # 爬取的时间

    def get_insert_sql(self):
        insert_sql = '''
                    insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
                    watch_user_num, follower_num, crawl_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
                    watch_user_num=VALUES(watch_user_num), follower_num=VALUES(follower_num)
                '''
        zhihu_id = self['zhihu_id'][0]
        topics = ','.join(self['topics'])
        url = ''.join(self['url'])  # 因为里面就只有一个内容，所以这么写等同于self['url'][0]
        title = self['title'][0]
        content = self['content'][1] if self['content'][1] else self['content'][0]
        answer_num = extract_num(self['answer_num'][0])
        comments_num = extract_num(self['comments_num'][0])
        follower_num = self['watch_user_num'][0]
        watch_user_num = self['watch_user_num'][1]
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                    watch_user_num, follower_num, crawl_time)
        return insert_sql, params

class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答item
    zhihu_id = scrapy.Field()  # 本answer的id
    url = scrapy.Field()  # 本answer的url
    question_id = scrapy.Field()  # 就是ZhihuQuestionItem的zhihu_id
    author_id = scrapy.Field()
    content = scrapy.Field()
    voteup_num = scrapy.Field()  # 投票数
    comments_num = scrapy.Field()  # 评论数
    create_time = scrapy.Field()  # 创建时间
    update_time = scrapy.Field()  # answer的更新时间
    crawl_time = scrapy.Field()  # 抓取时间

    def get_insert_sql(self):
        insert_sql = '''
                    insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, voteup_num,
                    comments_num, create_time, update_time, crawl_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), voteup_num=VALUES(voteup_num), 
                    comments_num=VALUES(comments_num), create_time=VALUES(create_time), update_time=VALUES(update_time)
                '''
        create_time = datetime.datetime.fromtimestamp(self['create_time']).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self['update_time']).strftime(SQL_DATETIME_FORMAT)
        params = (self['zhihu_id'],self['url'], self['question_id'], self['author_id'], self['content'],
                  self['voteup_num'], self['comments_num'], create_time, update_time, self['crawl_time'], )
        return insert_sql, params

class LagouItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()

def remove_splash(value):
    #去掉字段的斜线/
    return value.replace('/','')

def remove_space(value):
    lis = value.split('\n')
    lis = [item.strip() for item in lis if item.strip() != '查看地图']
    return ''.join(lis)

class LagouJobItem(scrapy.Item):
    title = scrapy.Field()  # 职位
    url = scrapy.Field()
    url_md5 = scrapy.Field()  #
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_space),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_space),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
                    insert into lagou_job(title, url, url_md5, salary, job_city, work_years, degree_need, job_type, 
                    publish_time, job_advantage, job_desc, job_addr, company_name, company_url, tags, crawl_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE salary=VALUES(salary)
                '''
        params =(
            self['title'], self['url'], self['url_md5'], self['salary'], self['job_city'], self['work_years'],
            self['degree_need'], self['job_type'], self['publish_time'], self['job_advantage'], self['job_desc'],
            self['job_addr'], self['company_name'], self['company_url'], self['tags'], self['crawl_time']
        )
        return insert_sql, params