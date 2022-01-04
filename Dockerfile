FROM ubuntu:20.04

RUN apt update

## START - Creating user
RUN apt-get -y install sudo
RUN adduser --disabled-password --gecos '' docker
RUN adduser docker sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
## END - Creating user


## START - Install python
RUN apt-get install -y  python3 \
                    python3-pip
ADD requirements.txt .
RUN pip3 install -r requirements.txt
## END - Install python

## START - Setup project
RUN python3 src/setup.py
## END - Setup project


USER docker
WORKDIR /home/docker/projects

CMD [ "django-admin runserver" ]