# EMNS-DCT: An Audio Remote Creation and Validation Tool for Researchers

EMNS-DCT is a Django-based web tool that facilitates the creation and validation of audio remotely for researchers. It uses Docker for deployment and allows researchers to create, record, and validate audio utterances with ease.

## Prerequisite

The EMNS-DCT tool requires the following prerequisites to be installed:

- `Docker`
- `docker-compose`

## Getting Started

### Enviroment Variables

Before running the tool, you need to set the environment variables in the env_variables.conf file. The following environment variables are required:

- `SECRET_KEY`: A secret key for Django
- `ALLOWED_HOSTS`: A comma-separated list of allowed hosts
- `EMAIL_USER`: Email ID for sending email notifications
- `EMAIL_PASS`: Password for email account

### Docker

Docker is used for deploying the tool. Once you have Docker and docker-compose installed, you can build and run the tool using the provided Makefile. Here are some useful commands to get started:

- `make build`: Build the Docker container
- `make run`: Start the Docker container
- `make restart`: Restart the Docker container
- `make down`: Stop and remove the Docker container

### Reset migrations

If you want to reset the migrations, you can use the following commands:

``` bash
find . -path "*/*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/*/migrations/*.pyc"  -delete
find . -path "*/db.sqlite3"  -delete
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Collect static file

If there are changes to static files, run the following command to collect them:

``` bash
python manage.py collectstatic
```

### Create Utterances

To create utterances for recording, validation etc, use the following commands, the function expect a `.tsv` file containing the `transcript` and `emotion`.

``` bash
cd dataset_collection_tool/django_dataset_collection_tool
python manage.py shell
```

``` python
from audio_recorder.models import Utterances
from django.contrib.auth.models import User
import random
import pandas as pd


def create_utterance(user, utterance, prosody):
 post = Utterances( utterance=utterance,
      prosody=prosody,
      author=user)
 post.save()

def main(csv_dir, sep="\t", emotions=None):
 if emotions==None:
  emotions = ['Happy', 'Sad', 'Angry', 'Excited', 'Sarcastic', 'Neutral', 'Disgust', 'Surprised']
 
 user = User.objects.filter(username="knoriy").first()
 df = pd.read_csv(csv_dir, sep=sep, header=None).head(20_000)
 
 for i, row in df.iterrows():
  if not row.isnull().any():
   create_utterance(user, row[0], row[1])
  else:
   create_utterance(user, row[0], random.choice(emotions))
   print("Found nan: ", i)

main("/app/src/data/train.tsv")
```

### Start container

After you have created the utterances, you can start the container with the following command:

``` bash
make run
```

### Create ssl certificate

To create an SSL certificate, you can use the following commands:

``` bash
docker exec -it dataset_collection_tool_proxy_1 sh
```

``` bash
certbot --nginx --noninteractive --agree-tos -m name@email.com -d emns.com -d www.emns.com --redirect --test-cert
```

Remove `--test-cert` after confirming that everything loaded as expected.
