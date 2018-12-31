# coding=utf8
import pymysql
from pyecharts import Bar
from django_echarts.views.backend import EChartsBackendView
from django_echarts.datasets.charts import NamedCharts

class BackendEChartsTemplate(EChartsBackendView):    
    echarts_instance_name = 'echarts_instance'
    client = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',  
        passwd='root', 
        db='cfda_drugs',
        charset='utf8'   
    )
    cur = client.cursor()
    

    def get_template_names(self):        
        if self.keyword and self.hasresult:
            self.template_name = 'drugs/backend_charts.html'
        else:
            self.template_name = 'drugs/index.html'
        return super().get_template_names()

    def get_echarts_instance(self, *args, **kwargs):
        self.hasresult = False 
        self.keyword = self.request.GET.get('q')       
        print('keyword = {}'.format(self.keyword))
        if not self.keyword: return None            
        # print(bar.__class__)
        # cur.execute('select id, address, production_unit_name from production_units where production_unit_name like %s', '%四川%')
        self.cur.execute("select res.year, count(*) as counts from \
        (select drug_name_zh, date_format(approval_date, '%Y') as year from drugs_approved where drug_name_zh like '{}') as res \
        group by res.drug_name_zh, res.year".format(self.keyword))
        # cur.execute("select drug_name_zh, date_format(approval_date, '%Y') as year from drugs_approved where drug_name_zh like '%氯化钠注射液%'")
        result = self.cur.fetchall()
        print('result = {}'.format(result))
        echarts_instance = NamedCharts()
        if not result:
            return None
        self.hasresult = True
        ds, hs = zip(*result)
        bar = Bar(self.keyword, "这里是副标题")        
        bar.add(self.keyword, ds, hs)
        bar.add('copy', ds, hs)
        echarts_instance = echarts_instance.add_chart(bar, name='pieo')
        bar2 = Bar("我的第2个图表", "这里是副标题")
        # print(bar2.__class__)
        bar2.add("服装", ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"], [5, 20, 36, 10, 75, 90])
        echarts_instance = echarts_instance.add_chart(bar2, name='piet')

        return echarts_instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q') or ''
        return context