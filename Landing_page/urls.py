from django.urls import path
from .views import dynamic_form_view
from . import views


urlpatterns = [
    path('dynamic_form_view/', dynamic_form_view, name='dynamic_form'),
    path('', views.index, name='index'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('we_do', views.we_do, name='we_do'),
    path('about', views.about, name='about'),

]