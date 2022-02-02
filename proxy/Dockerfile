FROM nginxinc/nginx-unprivileged:stable-alpine


COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params

USER root

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static

RUN apk add certbot certbot-nginx

# USER nginx