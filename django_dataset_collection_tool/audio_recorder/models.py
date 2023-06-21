from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import detail
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid

# from django_dataset_collection_tool.audio_recorder.views import utterances

class Utterances(models.Model):
    utterance       = models.TextField()
    description     = models.TextField(null=True)
    bg_sounds       = models.CharField(max_length=70, default='', null=True)
    accent          = models.CharField(max_length=70, default='')
    emotion         = models.TextField(default='')
    author          = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date_created    = models.DateTimeField(default=timezone.now)
    status          = models.CharField(max_length=70, null=True, choices=(('Pending', 'Pending'), ('Awaiting Review', 'Awaiting Review'), ('Complete', 'Complete'), ('Needs Updating', 'Needs Updating' )), default='Pending' )
    gender          = models.CharField(max_length=70, null=True, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), default='Female')
    audio_quality   = models.CharField(max_length=70, null=True, choices=(('Unusable', 'Unusable'), ('Poor', 'Poor'), ('Average', 'Average'), ('Good', 'Good'), ('Excellent', 'Excellent')))
    age             = models.CharField(max_length=70, null=True)
    arousal         = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    valence         = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    audio_recording = models.FileField(upload_to='media/')

    locked_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='locked_utterances')
    is_locked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.utterance}"

    def get_absolute_url(self):
        return reverse('utterance-detail', kwargs={'pk':self.pk})

    def save(self, *args, **kwargs):
        if self.pk:
            recording = Utterances.objects.get(pk=self.pk)
            if recording.audio_recording != self.audio_recording:
                recording.audio_recording.delete(save=False)
        super().save(*args, **kwargs)

    def acquire_lock(self, user):
        if self.author is None:
            self.author = user
            self.save()
            return True
        return False

    def release_lock(self, user):
        if self.author == user:
            self.author = None
            self.save()