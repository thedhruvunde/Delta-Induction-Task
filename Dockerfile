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
    && rm -rf /var/lib/apt/lists/*

COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh
EXPOSE 80
