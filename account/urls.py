from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('login/', views.login, name='login'),
    path("password_change", views.password_change, name="password_change"),
    path('profile/<username>', views.profile, name='profile'),
    path('logout/', views.custom_logout, name='logout'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),
]