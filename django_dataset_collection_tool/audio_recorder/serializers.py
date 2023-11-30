from rest_framework import serializers
from .models import Utterances

class UtteranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utterances
        fields = '__all__'
        read_only_fields = ['author']