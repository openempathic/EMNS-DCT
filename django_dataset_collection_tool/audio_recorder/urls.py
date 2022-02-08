from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView, name="audio-recorder-home"),
    path('contact-us/', views.ContactUsView.as_view(), name="contact-us"),

    path('utterances/', views.UtteranceListView.as_view(), name="audio-recorder-utterances"),
    path('utterances/user/<username>/', views.UserUtteranceListView.as_view(), name="user-utterances"),
    path('utterances/export/', views.Export.as_view(), name="export-utterances"),
    path('utterances/import/', views.Import.as_view(), name="import-utterances"),


    
    path('utterances/<int:pk>/', views.UtteranceDetailView.as_view(), name="utterance-detail"),

    path('utterances/<int:pk>/update/', views.UtteranceUpdateView.as_view(), name="utterance-update"),

    path('utterances/<int:pk>/delete/', views.UtteranceDeleteView.as_view(), name="utterance-delete"),
    path('utterances/new/', views.UtteranceCreateView.as_view(), name="utterance-create"),
]

handler404 = 'audio_recorder.views.handler404'