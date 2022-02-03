# FROM httpd:2.4
FROM ubuntu:20.04

RUN apt update

## START - Creating user
RUN apt-get -y install sudo
RUN adduser --disabled-password --gecos '' user
RUN adduser user sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
## END - Creating user

## START - Install nginx
RUN apt install -y nginx  systemctl
# COPY ./default.conf /etc/nginx/conf.d/default.conf
# COPY ./uwsgi_params /etc/nginx/uwsgi_params
## END - Install nginx

RUN apt install -y certbot python3-certbot-nginx

USER user

CMD ["sudo systemctl start nginx" ]

# CMD [ "certbot --nginx --noninteractive --agree-tos -m knoriy72@gmail.com -d dct.knoriy.com -d www.dct.knoriy.com" ]