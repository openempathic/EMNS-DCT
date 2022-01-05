from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="audio-recorder-record"),
    path('about/', views.about, name="audio-recorder-about"),

]
