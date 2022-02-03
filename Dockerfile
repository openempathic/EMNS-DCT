FROM ubuntu:20.04

RUN apt update

## START - Creating user
RUN apt-get -y install sudo
RUN adduser --disabled-password --gecos '' user
RUN adduser user sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
## END - Creating user

## START - Python packages
RUN apt install -y python3.8 python3-pip
ADD requirements.txt .
RUN pip install -r requirements.txt
## END - Python packages

USER user

CMD [ "bash" ]