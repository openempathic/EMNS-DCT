from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="audio-recorder-home"),
    path('about/', views.about, name="audio-recorder-about"),
    path('utterances/', views.UtteranceListView.as_view(), name="audio-recorder-utterances"),
    path('utterances/user/<username>', views.UserUtteranceListView.as_view(), name="user-utterances"),

    path('utterances/<int:pk>/', views.UtteranceDetailView.as_view(), name="utterance-detail"),
    path('utterances/<int:pk>/update/', views.UtteranceUpdateView.as_view(), name="utterance-update"),
    # path('utterances/<int:pk>/update-recording/', views.UtteranceUpdateRecordingView.as_view(), name="utterance-update-recording"),

    path('utterances/<int:pk>/delete/', views.UtteranceDeleteView.as_view(), name="utterance-delete"),
    path('utterances/new/', views.UtteranceCreateView.as_view(), name="utterance-create"),
]


handler404 = 'audio_recorder.views.handler404'