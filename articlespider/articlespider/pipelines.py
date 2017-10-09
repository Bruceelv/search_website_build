# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs, json
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if 'front_img_path' in item:
            for ok, value in results:
                img_file_path = value['path']
                item['front_img_path'] = img_file_path
        return item


class ElasticsearchPipelines(object):
    #将数据写入到ES中
    def process_item(self, item, spider):
        #讲item转为es数据
        item.save_to_es()
        return item



