from django.urls import path

from . import views
from polls.echart_views import BackendEChartsTemplate

urlpatterns = [
    # ex: /polls/
    path('', BackendEChartsTemplate.as_view()),
    # path('^\?.*.$', BackendEChartsTemplate.as_view()),
    # ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]