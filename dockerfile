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
    vim
COPY webapp /webapp

RUN mkdir -p /var/log/supervisor

ENV MYSQL_PASSWORD= MYSQL_USER= MYSQL_DATABASE= MYSQL_HOST= PIP_USE_PEP517=1

RUN pip3 install --quiet --upgrade pip && pip3 install --quiet --upgrade setuptools && pip3 install --quiet -r /webapp/requirements.txt

EXPOSE 8080 80

WORKDIR /webapp

ENTRYPOINT ["supervisord", "--nodaemon", "--configuration", "/webapp/supervisord.conf"]
