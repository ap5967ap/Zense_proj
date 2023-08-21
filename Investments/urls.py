from django.urls import path
from . import views

urlpatterns=[
    path('',views.investment_summary,name="investment_summary"),
    path("previous_investment/",views.previous_investment,name="previous_investment"),
    path("mf_home/",views.mf_home,name="mf_home"),
    path('mf_recomm',views.mf_recomm,name="mf_recomm"),
    path('mf_predict',views.mf_predict,name="mf_predict"),
    path('mf_transact/',views.mf_transact,name='mf_transact'),
    path('mf_single/<str:name>',views.mf_single,name='mf_single'),
    path('mf_data_single/<str:name>',views.mf_data_single,name='mf_data_single'),
    path('mf_prev/',views.mf_prev,name='mf_prev'),
    path('mf_sell/',views.mf_sell,name='mf_sell'),
    path('sold_prev/',views.sold_prev,name='sold_prev'),
    path('stock_predict/',views.stock_predict,name='stock_predict'),
    path('stock_recomm/',views.stock_recomm,name='stock_recomm'),
    path('stock_home/',views.stock_home,name='stock_home'),
    path('stock_transact/',views.stock_transact,name='stock_transact'),
    path('stock_prev/',views.stock_prev,name='stock_prev'),
]
