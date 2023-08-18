from django.urls import path
from . import views

urlpatterns=[
    path('',views.investment_summary,name="investment_summary"),
    path("mf_home/",views.mf_home,name="mf_home"),
    path("previous_investment/",views.previous_investment,name="previous_investment"),
]
