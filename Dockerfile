FROM ubuntu:20.04

RUN apt update

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata

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

ENV PATH="/scripts:${PATH}"
COPY ./scripts /scripts
RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web

# USER user
WORKDIR /app

CMD ["entrypoint.sh"]