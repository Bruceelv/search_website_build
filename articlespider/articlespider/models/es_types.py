
from elasticsearch_dsl import DocType, Date, Nested, Boolean,\
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

connections.create_connection(hosts=['localhost'])  # 创建链接

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer('ik_max_word', filter=['lowercase'])

class ArticleType(DocType):
    #伯乐在线文章类型
    suggest = Completion(analyzer=ik_analyzer)  # 自动不全的字段
    title = Text(analyzer='ik_max_word')
    create_date = Date()
    zan = Integer()
    store = Integer()
    comments = Integer()
    contents = Text(analyzer='ik_max_word')
    tags = Text(analyzer='ik_max_word')
    front_img_url = Keyword()
    front_img_path = Keyword()
    url = Keyword()
    url_md5 = Keyword()

    class Meta:
        index = 'jobbole'
        doc_type = 'article'

if __name__ == '__main__':
    ArticleType.init()