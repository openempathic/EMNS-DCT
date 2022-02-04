FROM nginxinc/nginx-unprivileged:1-alpine

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params

USER root

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static

RUN apk add certbot certbot-nginx
RUN mkdir /etc/letsencrypt
RUN chmod 755 /etc/letsencrypt

# RUN certbot --nginx --test-cert --noninteractive --agree-tos -m knoriy72@gmail.com -d dct.knoriy.com -d www.dct.knoriy.com --redirect

# USER nginx