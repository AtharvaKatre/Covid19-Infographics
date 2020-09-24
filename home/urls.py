from django.contrib import admin
from django.urls import path
from home import views
from home.dash_apps.finished_apps import engine

urlpatterns = [
    path('', views.index, name='index'),
    path('india', views.india, name='india'),
    path('testing_labs', views.testing_labs, name='testing_labs'),
    path('about',views.about, name='about'),



]
