from django.urls import path
from . import views

urlpatterns = [
    path('', views.balance, name='balance'),
    path('profile/', views.profile, name='profile')
]