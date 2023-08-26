from django.urls import path
from . import views,analysis

urlpatterns = [
    path("add_income/", views.add_income, name="add_income"),
    path("view_income/", views.view_income, name="view_income"),
    path("edit_income/<int:id>/", views.edit_income, name="edit_income"),
    path("delete_income/<int:id>/", views.delete_income, name="delete_income"),
    path("add_object_income/<int:id>/", views.add_object_income, name="add_object_income"),
    path("delete_source_income/<str:source>/", views.delete_source_income, name="delete_source_income"),
    path("analyse_single/<int:id>/", analysis.analysis_single, name="analyse_single"),
    path("chart/<str:source>/", analysis.single_analysis, name="chart"),
    path("income_summary/",views.income_summary,name="income_summary"),
    path("income_summary_data/",views.income_summary_data,name="income_summary_data"),
]