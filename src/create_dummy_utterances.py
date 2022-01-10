from audio_recorder.models import Utterances
from django.contrib.auth.models import User

user = User.objects.filter(username="knoriy").first()

for i in range (10,100):
    post = Utterances(  utterance=f"Hellow World! {i+1}",
                        prosody=f"happy {i+1}",
                        author=user)
    post.save()

Utterances.objects.all()