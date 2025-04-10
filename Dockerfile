FROM ghcr.io/astral-sh/uv:alpine

RUN apk add --update gcc musl-dev openldap-dev python3-dev bash

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /var/www && mkdir /var/www/python-workload
WORKDIR /var/www/python-workload

COPY . .

RUN uv run sync
RUN uv run manage.py migrate

CMD ["uv", "run", "gunicorn", "core.wsgi"]
