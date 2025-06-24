FROM debian:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    wget \
    curl \
    unzip \
    git \
    vim \
    inotify-tools\
    jq\
    nginx\
    postgresql\
    postgresql-contrib\
    python3-pip\
    python3-psycopg2\
    libpq-dev\
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pyyaml psycopg2-binary

COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh
EXPOSE 80
