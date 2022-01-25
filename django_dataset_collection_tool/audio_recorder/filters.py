from dataclasses import field
import django_filters

from .models import Utterances

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Utterances
        fields = {  'prosody':['contains'], 
                    'status':['exact']
                    }

        # exclude = ['audio_recording']