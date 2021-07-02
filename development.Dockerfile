FROM python:3.8.0-alpine

WORKDIR /usr/src/graph

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache --virtual build-deps curl gcc g++ libffi-dev make postgresql-dev postgresql-client bash

ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/graph/requirements.txt
RUN pip install -r requirements.txt

COPY /graph /usr/src/graph/

ENTRYPOINT ["/usr/src/graph/entrypoint.sh"]
