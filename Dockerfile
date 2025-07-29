FROM ghcr.io/astral-sh/uv:alpine

RUN apk add --update gcc linux-headers musl-dev openldap-dev python3-dev bash make

# set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the directory for the code and jump into it
RUN mkdir /var/www && mkdir /var/www/physics-workload
WORKDIR /var/www/physics-workload

# Copy across the project details and build the project environment
COPY pyproject.toml uv.lock README.md ./
RUN uv run sync

# Copy across the rest of the files
COPY . .
