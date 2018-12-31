# coding=utf8
import pymysql
from pyecharts import Bar
from django_echarts.views.backend import EChartsBackendView
from django_echarts.datasets.charts import NamedCharts

class BackendEChartsTemplate(EChartsBackendView):
    template_name = 'polls/backend_charts.html'
    echarts_instance_name = 'echarts_instance'
    client = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',  #使用自己的用户名 
        passwd='root',  # 使用自己的密码
        db='cfda_drugs',  # 数据库名
        charset='utf8'   
    )
    cur = client.cursor()


    def get_echarts_instance(self, *args, **kwargs):
        # keyword = self.request.GET.get('q')
        keyword = '氯化钠注射液'
        print('keyword = {}'.format(keyword))
        if keyword:
            bar = Bar(keyword, "这里是副标题")
            # print(bar.__class__)
            # cur.execute('select id, address, production_unit_name from production_units where production_unit_name like %s', '%四川%')
            self.cur.execute("select res.year, count(*) as counts from \
            (select drug_name_zh, date_format(approval_date, '%Y') as year from drugs_approved where drug_name_zh like '{}') as res \
            group by res.drug_name_zh, res.year".format(keyword))
            # cur.execute("select drug_name_zh, date_format(approval_date, '%Y') as year from drugs_approved where drug_name_zh like '%氯化钠注射液%'")
            result = self.cur.fetchall()
            ds, hs = zip(*result)
    
            bar.add(keyword, ds, hs)
            bar.add('copy', ds, hs)
    
            bar2 = Bar("我的第2个图表", "这里是副标题")
            print(bar2.__class__)
            bar2.add("服装", ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"], [5, 20, 36, 10, 75, 90])
            echarts_instance = NamedCharts().add_chart(bar, name='pieo').add_chart(bar2, name='piet')    
            return echarts_instance


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q') or ''
        return context