from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="audio-recorder-home"),
    path('about/', views.about, name="audio-recorder-about"),
    path('record/', views.record, name="audio-recorder-record"),


]
