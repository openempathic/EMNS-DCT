from audio_recorder.models import Utterances, SampleUtterances
from django.contrib.auth.models import User
import glob
import pathlib
import json
import os
import random

def create_sample_utterance(user, utterance, audio):
	post = SampleUtterances(test=utterance,
						)
	post.save()

def create_utterance(user, utterance, audio):
	post = Utterances(	utterance=utterance,
						audio_recording=audio,
						author=user)
	post.save()

def main(sample:bool=False):
	user = User.objects.filter(username="knoriy").first()
	paths = glob.glob("media/**/*.json")
	random.shuffle(paths)
	if sample:
		paths = paths[:10]
	print(paths)
	for path in paths:
		path = pathlib.Path(path)
		with open(path) as f:
			meta = json.load(f)
			audio_file_path = os.path.join('media', path.parent.name, path.stem+'.flac')
	if sample:
		create_sample_utterance(user, meta['text'], audio_file_path)
	else:
		create_utterance(user, meta['text'], audio_file_path)

def youtube(sample:bool=False):
	user = User.objects.filter(username="knoriy").first()
	paths = [
		'https://www.youtube.com/embed/60VguVRiYmw?start=30&end=60&modestbranding=1&controls=0&disablekb=1&loop=1', 
		'https://www.youtube.com/embed/60VguVRiYmw?start=60&end=120&modestbranding=1&controls=0&disablekb=1&loop=1',
		]
	random.shuffle(paths)
	for i, path in enumerate(paths):
		create_utterance(user, f"This is test for youtube links, {i}", path)


if __name__ == '__main__':
	main(True)