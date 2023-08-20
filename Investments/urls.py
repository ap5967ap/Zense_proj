from django.urls import path
from . import views

urlpatterns=[
    path('',views.investment_summary,name="investment_summary"),
    path("mf_home/",views.mf_home,name="mf_home"),
    path('mf_recomm',views.mf_recomm,name="mf_recomm"),
    path('mf_predict',views.mf_predict,name="mf_predict"),
    path("previous_investment/",views.previous_investment,name="previous_investment"),
    path('mf_transact/',views.mf_transact,name='mf_transact'),
    path('mf_single/<str:name>',views.mf_single,name='mf_single'),
    path('mf_data_single/<str:name>',views.mf_data_single,name='mf_data_single'),
    path('mf_prev/',views.mf_prev,name='mf_prev'),
    path('mf_sell/',views.mf_sell,name='mf_sell'),
]
