FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

# RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apk -y add tzdata


COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN pip install -r /requirements.txt
RUN apk del .tmp

COPY ./django_dataset_collection_tool/ /app
WORKDIR /app
COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
# RUN chown -R user:user /app/static


# USER user

CMD ["entrypoint.sh"]
