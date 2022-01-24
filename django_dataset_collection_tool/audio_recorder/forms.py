from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Utterances


class RecordingUpdateForm(forms.ModelForm):
    class Meta:
        model = Utterances
        fields = ['prosody']
        fields = []


