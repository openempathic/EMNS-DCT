FROM nginxinc/nginx-unprivileged:stable-alpine

USER root

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static

USER nginx