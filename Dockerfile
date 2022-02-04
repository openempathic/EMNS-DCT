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

# ## START - Nginx
# RUN apt install -y nginx systemctl
# COPY ./proxy/default.conf /etc/nginx/conf.d/default.conf
# # COPY ./proxy/uwsgi_params /etc/nginx/uwsgi_params
# RUN systemctl start nginx
# ## END - Nginx

# ## START - Certbot
# RUN apt install -y certbot python3-certbot-nginx
# # RUN certbot --nginx --test-cert --noninteractive --agree-tos -m knoriy72@gmail.com -d dct.knoriy.com -d www.dct.knoriy.com --redirect
# ## END - Certbot

USER user
WORKDIR /app

CMD ["entrypoint.sh"]