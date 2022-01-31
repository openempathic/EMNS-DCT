#!/bin/sh

set -e

python3 manage.py collectstatic --noinput

uwsgi --socket :8000 --master --enable-threads --module app.wsgi