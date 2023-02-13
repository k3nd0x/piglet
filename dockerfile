FROM alpine:3.17.1
RUN apk add --update \
    build-base \
    python3-dev \
    python3 \
    libffi-dev \
    openssl-dev \
    py3-pip \
    supervisor \
    mysql-client \
    vim \
    redis

COPY webapp /webapp

WORKDIR /webapp

ENV MYSQL_PASSWORD= MYSQL_USER= MYSQL_DATABASE= MYSQL_HOST= PIP_USE_PEP517=1 DOMAIN= MAIL_SERVER= MAIL_PORT= MAIL_USER= MAIL_PASSWORD= MAIL_ENCRYPTIONPROTOCOL=

#RUN pip3 install --quiet --upgrade pip && pip3 install --quiet --upgrade setuptools && pip3 install --quiet -r /webapp/requirements.txt

EXPOSE 8080 80

ENTRYPOINT ["supervisord", "--nodaemon", "--configuration", "/webapp/supervisord.conf"]
