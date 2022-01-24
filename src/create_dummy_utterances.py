from audio_recorder.models import Utterances
from django.contrib.auth.models import User

user = User.objects.filter(username="knoriy").first()
testuser = User.objects.filter(username="testuser").first()

for i in range (1,100):
    post = Utterances(  utterance=f"Hellow World! {i:03}",
                        prosody=f"happy {i:03}",
                        author=user)
    post.save()

Utterances.objects.all()