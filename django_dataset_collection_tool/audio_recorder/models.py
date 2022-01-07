from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Utterances(models.Model):
    utterance       = models.TextField()
    prosody         = models.CharField(max_length=70)
    author          = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date_created    = models.DateTimeField(default=timezone.now)

    audio_recording = models.FileField()


    def __str__(self) -> str:
        return self.utterance#, self.audio_recording