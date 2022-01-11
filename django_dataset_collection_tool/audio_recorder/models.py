from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import detail

# from django_dataset_collection_tool.audio_recorder.views import utterances

class Utterances(models.Model):
    utterance       = models.TextField()
    prosody         = models.CharField(max_length=70)
    author          = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date_created    = models.DateTimeField(default=timezone.now)

    audio_recording = models.FileField(upload_to='media/wavs')

    def __str__(self) -> str:
        return f"{self.utterance}, Prosody: {self.prosody}"

    def get_absolute_url(self):
        return reverse('utterance-detail', kwargs={'pk':self.pk})