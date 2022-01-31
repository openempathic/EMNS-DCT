from django.contrib import admin
from .models import Utterances
from import_export import resources


admin.site.register(Utterances)



class UtterancesResource(resources.ModelResource):
    class Meta:
        model = Utterances
        fields = ['utterance', 'prosody', 'author', 'date_created', 'status', 'audio_recording']