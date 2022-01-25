from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import random
import pandas as pd


def create_utterance(user, utterance, prosodies):

    post = Utterances(  utterance=utterance,
                        prosody=random.choice(prosodies),
                        author=user)
    post.save()

def read_csv():
    pd.read_csv()


if __name__ == '__main__':
    prosodies = ['Happy', 'Sad', 'Angry', 'Excited']
    user = User.objects.filter(username="knoriy").first()



    create_utterance(user, prosodies)