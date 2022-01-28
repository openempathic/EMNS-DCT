from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import random
import pandas as pd


def create_utterance(user, utterance, prosody):
	post = Utterances(	utterance=utterance,
						prosody=prosody,
						author=user)
	post.save()

def main():
	prosodies = ['Happy', 'Sad', 'Angry', 'Excited']
	user = User.objects.filter(username="knoriy").first()
	df = pd.read_csv("/home/knoriy/Documents/phd/dataset_collection_tool/src/dummy_utterances.csv", sep="|")
	print(df)
	print('#'*100)
	for i, row in df.iterrows():
		if not row.isnull().any():
			create_utterance(user, row['Transcription'], row['Prosody'])
		else:
			create_utterance(user, row['Transcription'], random.choice(prosodies))
			print("Found nan: ", i)

create_utterance(user, 'Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!Super duper long test that will not fill the card in my utteracne filter template, Hopefulyl!!', 'happy')