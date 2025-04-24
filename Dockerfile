FROM ghcr.io/astral-sh/uv:alpine

RUN apk add --update gcc musl-dev openldap-dev python3-dev bash

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /var/www && mkdir /var/www/physics-workload
WORKDIR /var/www/physics-workload

COPY . .

RUN uv run sync
RUN uv run manage.py makemigrations && uv run manage.py migrate
RUN uv run manage.py collectstatic --noinput
