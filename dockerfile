FROM alpine:latest
RUN apk add --update \
    build-base \
    python3-dev \
    python3 \
    libffi-dev \
    openssl-dev \
    py3-pip \
    supervisor \
    sqlite \
    vim \
    mysql-client \
    redis 

ENV MYSQL_PASSWORD=9vaGPf8fXzdexm5DM2 MYSQL_USER=piglet MYSQL_DATABASE=piglet MYSQL_HOST=database PIP_USE_PEP517=1 DOMAIN=localhost MAIL_SERVER= MAIL_PORT= MAIL_USER= MAIL_PASSWORD= MAIL_ENCRYPTIONPROTOCOL= SECURE_COOKIE=False DB_ROOT_PASSWORD=xUDEZMKWew9D3hn27ZRKSdGw

COPY webapp/config/python/requirements.txt /tmp/requirements.txt

RUN pip3 install --quiet -r /tmp/requirements.txt --break-system-packages

COPY webapp /webapp
RUN mkdir -p /webapp/log/api /webapp/log/app /webapp/log/scheduler
WORKDIR /webapp

EXPOSE 8080 80 5566

ENTRYPOINT ["supervisord", "--nodaemon", "--configuration", "/webapp/config/supervisor/supervisord.conf"]
