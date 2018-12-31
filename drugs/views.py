import pymysql, json
from pyecharts import Bar
from django_echarts.views.backend import EChartsBackendView
from .front_views import FrontEChartsTemplate
from django_echarts.datasets.charts import NamedCharts
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db.models.functions import ExtractYear
from django.db.models import Count, Max, Min
from .models import DrugsApproved
from .dataset import DrugDataset
from django.shortcuts import render_to_response, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_exempt,csrf_protect #Add this

ddset = DrugDataset()

class BackendEChartsTemplate(EChartsBackendView):    
    # echarts_instance_name = 'echarts_instance'
    model = DrugsApproved
    hasresult = False
    
    def get_template_names(self):        
        if self.keyword and self.hasresult:
            self.template_name = 'drugs/backend_charts.html'
        else:
            self.template_name = 'drugs/index.html'
        print('template_name: {}'.format(self.template_name))
        return super().get_template_names()

    def get_echarts_instance(self, *arg, **kwargs):
        if len(self.dataset) > 0:
            self.hasresult = True
            bar = Bar(self.cur_word, "按别名")
                # aggregate data count of each name from db, then order them
            ys, cs = zip(*self.dataset)
            bar.add(self.cur_word, ys, cs)
            print('bar = {}'.format(bar))
            echarts_instance = NamedCharts()
            echarts_instance = echarts_instance.add_chart(bar)
            return echarts_instance

    def get(self, request, *args, **kwargs):
        self.keyword =self.request.GET.get('q', '').strip()
        print('keyword:{}'.format(self.keyword))
        if self.keyword == '': return self.render_to_home()

        #self.querys is like [{'name':'someword', 'column':'column_name', 'active':False},...]
        self.dataset, self.querys, self.chart_by_name, self.chart_by_column, self.cur_word = ddset.get_datasets(self.keyword)
        if len(self.querys) == 0:
            return self.render_to_home()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'querys':self.querys,
            'q':self.keyword,
            'chart_by_name':self.chart_by_name,
            'chart_by_column':self.chart_by_column,
            'cur_word':self.cur_word,
            })
        return context

    def render_to_home(self):
        self.hasresult = False
        return self.render_to_response(context = {
            'q' : self.keyword,
            'noresult' : True,
            })

@csrf_exempt
def testmodel(request):
    print('post: {}'.format(request.POST))
    qset, qwords, columns = ddset.get_queryset(u'复方板蓝根颗粒')
    print(qset)
    print(qwords)
    return HttpResponse(str(qset[0]))

def index(request):
    return render_to_response('drugs/index.html')

def fronthome(request):
    keyword = request.GET.get('q', '').strip()
    if keyword=='':
        return redirect('index')
    datasets = {}
    querys, cur_word, qset = ddset.get_query_names(keyword)
    if querys == {}: return render_to_response('frontend_charts.html')
    qset = qset.order_by('-approval_date').values(*ddset.view_colnames)
    paginator = Paginator(qset, 20)
    qset_page = paginator.get_page(1)
    datasets={'querys':querys, 'q':cur_word, 'drugs_list_page':qset_page}
    return render_to_response('frontend_charts.html', datasets)

# def drugslist(request):
#     print('request.POST:', request.POST)
#     qcols= request.POST
#     qcols = {k:''.join(v) for k,v in qcols.items()}
#     print("qcols IN DrugsList:", qcols)
#     # SOME ERROR IN UPDATE DICT
#     # qcols={'盐酸雷尼替丁氯化钠注射液':'drug_name_zh'}.update(qcols)
#     # print("qcols IN DrugsList:", qcols)
#     qset = ddset.get_queryset_by_dict(**qcols).all()
#     # datas = json.dumps(qset.values()[:])    
#     data = serializers.serialize("json", qset)
#     print('data: ', data)
#     return JsonResponse(data=data, safe=False)

def drugslist(request, page):
    print('request.POST:', request.POST)
    qcols= request.POST
    qcols = {k:''.join(v) for k,v in qcols.items()}
    print("qcols IN DrugsList:", qcols)
    qset = ddset.get_queryset_by_dict(**qcols).order_by('-approval_date').values(*ddset.view_colnames)
    # print('qset: ', qset)
    paginator = Paginator(qset, 20)
    qset_page = paginator.get_page(page)
    res = render_to_response('drugs/drugs_list.html', {'drugs_list_page':qset_page})
    # print('res.content: ', res.content.decode())
    return JsonResponse(data={'drugs':res.content.decode()}, safe=False)
