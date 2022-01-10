from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="audio-recorder-home"),
    path('about/', views.about, name="audio-recorder-about"),
    path('utterances/', views.UtteranceListView.as_view(), name="audio-recorder-utterances"),
    path('record/<pk>/', views.UtteranceDetailView.as_view(), name="utterance-detail"),
]
