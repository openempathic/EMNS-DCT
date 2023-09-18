from audio_recorder.models import Utterances, SampleUtterances
from django.contrib.auth.models import User
from datasets import load_dataset
import glob
import pathlib
import json
import os
import random


def create_sample_utterance(user, utterance, audio):
	post = SampleUtterances(test=utterance,
						)
	post.save()

def create_utterance(user, utterance, audio, language):
	post = Utterances(	utterance=utterance,
						audio_recording=audio,
						language = language,
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

def youtube():
	user = User.objects.filter(username="knoriy").first()
	dataset = load_dataset('knoriy/OE-DCT-Movie-clips')
	for split in dataset.keys():
		for sample in dataset[split].shuffle(seed=42):
			create_utterance(user, sample['text'], sample['url'], sample['language'])
	


if __name__ == '__main__':
	youtube()