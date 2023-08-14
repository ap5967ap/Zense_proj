from django.urls import path
from . import views

urlpatterns = [
    path("add_income/", views.add_income, name="add_income"),
    path("view_income/", views.view_income, name="view_income"),
    path("edit_income/<int:id>/", views.edit_income, name="edit_income"),
    path("delete_income/<int:id>/", views.delete_income, name="delete_income"),
    path("add_object_income/<int:id>/", views.add_object_income, name="add_object_income"),
    path("delete_source_income/<str:source>/", views.delete_source_income, name="delete_source_income"),
]