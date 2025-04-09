from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('base/', views.base, name='base'),
    path('users/', views.users, name='users'),
    path('user_form_management/', views.user_form_management, name='user_form_management'),
    path('patients_management/', views.patients_management, name='patients_management'),
    path('users_management/', views.users_management, name='users_management'),
    path('user_reports/', views.user_reports, name='user_reports'),
    path('user_settings_management/', views.user_settings_management, name='user_settings_management'),


]

