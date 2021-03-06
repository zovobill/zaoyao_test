import pymysql, json
from pyecharts import Bar
from pyecharts_javascripthon.api import TRANSLATOR
from django_echarts.views.frontend import EChartsFrontView
from django_echarts.datasets.charts import NamedCharts
from django.http import HttpResponse, JsonResponse
from django.db.models.functions import ExtractYear
from django.db.models import Count, Max, Min
from .models import DrugsApproved
from django.shortcuts import render_to_response
from .dataset import DrugDataset
from django.views.generic import ListView
from django.core import serializers
import logging

ddset = DrugDataset()
logger = logging.getLogger('django')

class FrontEChartsTemplate(EChartsFrontView):    
    def get_echarts_instance(self, *arg, **kwargs):        
        logger.debug('POST: {}'.format(self.request.POST))
        logger.debug('kwargs: {}'.format(kwargs))

        qcols= self.request.POST
        keyword = qcols.get('cur_keyword', '')
        if '' != keyword:
            chartdatas, qwords, columns = ddset.get_datasets_by_dict(cur_keyword = keyword)
        else:
            qcols = {k:''.join(qcols[k]) for i,k in enumerate(qcols.keys()) if i < DrugDataset.MAX_KEYWORD_NUM}
            logger.debug("qcols:", qcols)            
            chartdatas, qwords, columns = ddset.get_datasets_by_dict(**qcols)
        charts = {}
        i = 1
        for chartid, chartdata in chartdatas.items():
            bar = Bar(chartid, "文号数量")
            # logger.debug('chartdata:', chartdata)
            # aggregate data count of each name from db, then order them
            for key, dataset in chartdata.items():
                try:
                    ys, cs = zip(*dataset)
                    bar.add(key, ys, cs, is_label_show=True)                 
                except:
                    pass
            # echarts_instance = NamedCharts()
            # echarts_instance = echarts_instance.add_chart(bar)

            if len(''.join(qcols.keys())) > 50:
                bar.options['legend'][0]['left'] = 100
            logger.debug('bar options.legend = {}'.format(bar.options['legend']))
            charts[i] = bar
            i += 1
        return charts

    def post(self, request, **kwargs):
        echarts = self.get_echarts_instance(**kwargs)
        datas = {}
        # logger.debug('echarts keys:', echarts.keys())
        for name, chart in echarts.items():

            datas[name] = TRANSLATOR.translate(chart.options).as_snippet()
            
            # logger.debug(name, chart.options['legend'])
            # logger.debug('*'*100)
        return JsonResponse(data=datas, safe=False)

    # def post(self, request, **kwargs):
    #     return self.get(request, **kwargs)

class DrugsList(ListView):
    """docstring for DrugsListView"""
    template_name = 'drugs/drugs_list.html'
    # context_object_name = 'durgs_list'

    # def get(self, request, *args, **kwargs):
    #     qcols= request.GET
    #     qcols = {k:''.join(v) for k,v in qcols.items()}
    #     logger.debug("qcols IN DrugsList:", qcols)
    #     # SOME ERROR IN UPDATE DICT
    #     # qcols={'盐酸雷尼替丁氯化钠注射液':'drug_name_zh'}.update(qcols)
    #     # logger.debug("qcols IN DrugsList:", qcols)
    #     qset = ddset.get_queryset_by_dict(**qcols)
    #     data = serializers.serialize("json", qset)
    #     return JsonResponse(data=data, safe=False)
    def get_queryset(self):
        qcols= self.request.POST
        qcols = {k:''.join(v) for k,v in qcols.items()}
        logger.debug("qcols IN DrugsList:", qcols)
        qset = ddset.get_queryset_by_dict(**qcols).all().values(*ddset.view_colnames)
        return qset

    # def get(self, request, *args, **kwargs):       
    #     context = self.get_context_data()
    #     return self.render_to_response(context)

    # def post(self, request, *args, **kwargs):       
    #     context = self.get_context_data()
    #     return self.render_to_response(context)