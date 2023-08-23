from django.urls import path
from . import views

urlpatterns = [
    path("add_wants/", views.add_wants, name="add_wants"),
    path("view_wants/", views.view_wants, name="view_wants"),
    path("edit_wants/<int:id>/", views.edit_wants, name="edit_wants"),
    path("delete_wants/<int:id>/", views.delete_wants, name="delete_wants"),
    path("add_object_wants/<int:id>/", views.add_object_wants, name="add_object_wants"),
    path("delete_source_wants/<str:source>/", views.delete_source_wants, name="delete_source_wants"),
    path("analyse_single_wants/<str:source>/", views.analysis_single_wants, name="analyse_single_wants"),
    path("chart_expense/<str:source>/", views.analysis_single_wants_data, name="chart_expense"),
    path("add_needs/", views.add_needs, name="add_needs"),
    path("single_needs/<str:source>/", views.single_needs, name="single_needs"),
    path("withdraw/<int:id>/", views.withdraw, name="withdraw"),
    path("add_need_to_expense/<int:id>/", views.add_need_to_expense, name="add_need_to_expense"),
    path("use_to_fund_other/", views.use_to_fund_other, name="use_to_fund_other"),
    path("add_need_to_investment/<int:id>/", views.add_need_to_investment, name="add_need_to_investment"),
    path("use_buffer/<int:id>/", views.use_buffer, name="use_buffer"),
    path("increase_buy_date/<int:id>/", views.increase_buy_date, name="increase_buy_date"),
    path("needs_view/", views.needs_view, name="needs_view"),
    path("change_priority/", views.change_priority, name="change_priority"),
]