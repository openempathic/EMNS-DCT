from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import glob
import pathlib
import json
import os
import random

def create_utterance(user, utterance, audio):
	post = Utterances(	utterance=utterance,
						audio_recording=audio,
						author=user)
	post.save()

def main():
	user = User.objects.filter(username="knoriy").first()
	paths = random.shuffle(glob.glob("media/**/*.json"))
	for path in paths:
		path = pathlib.Path(path)
		with open(path) as f:
			meta = json.load(f)
			audio_file_path = os.path.join('media', path.parent.name, path.stem+'.flac')
			create_utterance(user, meta['text'], audio_file_path)

main()