from django.contrib import admin
from django.urls import path
from home import views
from home.dash_apps.finished_apps import engine

urlpatterns = [
    path('', views.index, name='index'),
    path('states', views.states, name='states'),
    path('testing_labs', views.testing_labs, name='testing_labs'),
    path('about',views.about, name='about'),



]
