from django.urls import path
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page
from .views import BackendEChartsTemplate, testmodel, fronthome, index, drugslist
from .front_views import FrontEChartsTemplate, DrugsList
from django.views.decorators.csrf import csrf_exempt,csrf_protect #Add this

urlpatterns = [
    # ex: /drugs/
    # path('', BackendEChartsTemplate.as_view()),
    path('', index, name='index'),
    # path('options/', testmodel),
    path('search/', fronthome, name='fronthome'),
    # path('options/<str:keyword>/', FrontEChartsTemplate.as_view()),
    path('options/', csrf_exempt(FrontEChartsTemplate.as_view()), name = 'frontview'),
    # drugs list
    # path('list/', csrf_exempt(DrugsList.as_view()), name = 'drugslist'),
    path('list/<int:page>/', csrf_exempt(drugslist), name = 'drugslist'),   
]