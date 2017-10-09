from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
import json
from elasticsearch import Elasticsearch
from datetime import datetime

client = Elasticsearch(hosts=['127.0.0.1'])

# Create your views here.
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s','')  #接收前台输入的搜索词，准备到数据库查找
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest('my_suggest', key_words, completion={
                'field':'suggest','fuzzy':{
                    'fuzziness':2,
                },
                'size':10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source['title'])
        return HttpResponse(json.dumps(re_datas), content_type='application/json')

class SearchViews(View):
    def get(self, request):
        key_words = request.GET.get('q','')  # 接收前台传输过来的关键词
        page = request.GET.get('p','1')  # 接收前台传输过来的页码数，默认为1
        try:
            page = int(page)
        except:
            page = 1

        start_time = datetime.now()
        response = client.search(
            index='jobbole',
            body={
                # 搜索规则语法
                'query':{
                    'multi_match':{  # 采用多样化搜索
                        'query':key_words,  # 搜索关键词
                        'fields':['tags', 'title','content']  # 搜索的区域
                    }
                },
                #搜索之后的处理
                'from':(page-1)*10,   # 从第1、11……个显示，对应索引为0、10…
                'size':10,  #到第10个
                'highlight':{  # 高亮处理
                    'pre_tags': ['<span class="keyWord">'],  # 高亮关键字的起始标签，这里定义为span
                    'post_tags': ['</span>'],
                    'fields':{  # 高亮的区域：title、content
                        'title':{},
                        'content':{}
                    }
                }
            }
        )

        end_time = datetime.now()
        last_sec = (end_time - start_time).total_seconds()
        total_nums = response['hits']['total']
        hit_list = []  # 把搜索获取的数据在模板中作动态填充之用
        for hit in response['hits']['hits']:
            hit_dict = {}
            if 'title' in hit['highlight']:
                hit_dict['title'] = ''.join(hit['highlight']['title'])
            else:
                hit_dict['title'] = hit['_source']['title']
            if 'content' in hit['highlight']:
                hit_dict['content'] = ''.join(hit['highlight']['content'])[:500]
            else:
                hit_dict['content'] = hit['_source']['content'][:500]

            hit_dict['create_date'] = hit['_source']['create_date']
            hit_dict['url'] = hit['_source']['url']
            hit_dict['score'] = hit['_score']

            hit_list.append(hit_dict)
        if total_nums % 10 > 0:
            page_num = total_nums //10 + 1
        else:
            page_num = total_nums // 10
        print(page)
        return render(request, 'result.html', {"all_hits":hit_list,
                                                "key_words":key_words,
                                                "page":page,
                                                "total_nums":total_nums,
                                                "page_num":page_num,
                                                "last_sec":last_sec,})










