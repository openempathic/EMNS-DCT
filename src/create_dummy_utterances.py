from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import random

user = User.objects.filter(username="knoriy").first()
testuser = User.objects.filter(username="testuser").first()

prosodies = ['Happy', 'Sad', 'Angry', 'Excited']

for i in range (1,100):
    post = Utterances(  utterance=f"Hellow World!",
                        prosody=random.choice(prosodies),
                        author=user)
    post.save()

Utterances.objects.all()