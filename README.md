# Default

This container was tested on `Pop!_OS 20.04`.
Additinal changes may be required such as paths, please read the appropreate `README.md`.

# Prerequisite
## reset migrations
```
find . -path "*/*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/*/migrations/*.pyc"  -delete
find . -path "*/db.sqlite3"  -delete
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
## Collect static file
Only run this if static files are changed
```
python manage.py collectstatic
```
## Create Utterances
```
cd dataset_collection_tool/django_dataset_collection_tool
python manage.py shell
```
```
from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import random
import pandas as pd


def create_utterance(user, utterance, prosody):
	post = Utterances(	utterance=utterance,
						prosody=prosody,
						author=user)
	post.save()

def main(csv_dir, sep="\t", prosodies=None):
	if prosodies==None:
		prosodies = ['Happy', 'Sad', 'Angry', 'Excited', 'Sarcastic', 'Neutral', 'Disgust', 'Surprised']
	
	user = User.objects.filter(username="knoriy").first()
	df = pd.read_csv(csv_dir, sep=sep, header=None).head(20_000)
	
	for i, row in df.iterrows():
		if not row.isnull().any():
			create_utterance(user, row[0], row[1])
		else:
			create_utterance(user, row[0], random.choice(prosodies))
			print("Found nan: ", i)

main("/home/knoriy/Documents/phd/dataset_collection_tool/src/data/train.tsv")
```
## Start container
```
make run
```
## Create ssl certificate
```
docker exec -it dataset_collection_tool_proxy_1 sh
```
```
certbot --nginx --noninteractive --agree-tos -m knoriy72@gmail.com -d emns.knoriy.com -d www.emns.knoriy.com --redirect --test-cert
```
Remove `--test-cert` after confirming that everything loaded as expected.