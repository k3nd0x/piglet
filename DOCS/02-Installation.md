# :pig: 02-Installation

We try to keep the installation as smooth and easy as possible. Piglet is build for and with docker but you can also run it as a systemd service.

#### docker compose

Install `docker-compose` on your system and define your environment variables in the `.env` file:

```
### Required env Variables:
MYSQL_PASSWORD=changeme
MYSQL_USER=piglet
MYSQL_DATABASE=piglet
MYSQL_HOST=database # Default Hostname of the docker-compose database container
MYSQL_ROOT_PASSWORD=changeme
### Not required
MAIL_SERVER=''
MAIL_USER=''
MAIL_PASSWORD=''
MAIL_PORT=587
MAIL_ENCRYPTIONPROTOCOL=STARTTLS
DOMAIN=localhost
SECURE_COOKIE=False
```

Now the `docker-compose.yml` file. It spins up two docker container. Piglet itself and a mysql container. If you have a mysql instance already running you have to define host, user, root password and database name by yourself in the `.env` file.

```
services:
  piglet:
    restart: unless-stopped
    container_name: piglet
    depends_on:
      - database
    ports:
      - '0.0.0.0:80:80' # Piglet
    image: k3nd0x/piglet:latest
    environment:
      DB_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE} # Default 'piglet'
      MYSQL_USER: ${MYSQL_USER} # Default 'piglet'
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_HOST: ${MYSQL_HOST}
      MAIL_SERVER: ${MAIL_SERVER}
      MAIL_USER: ${MAIL_USER}
      MAIL_PASSWORD: ${MAIL_PASSWORD}
      MAIL_PORT: ${MAIL_PORT}
      MAIL_ENCRYPTIONPROTOCOL: ${MAIL_ENCRYPTIONPROTOCOL}
      DOMAIN: ${DOMAIN} # Default 'localhost'
      SECURE_COOKIE: ${SECURE_COOKIE}
    volumes:
      - "/etc/timezone:/etc/timezone:ro"
      - "/etc/localtime:/etc/localtime:ro"
  database:
    image: mariadb:11.1.2
    container_name: piglet-db
    volumes:
      - database-data:/var/lib/mysql
    environment:
      MARIADB_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MARIADB_DATABASE: ${MYSQL_DATABASE}
      MARIADB_USER: ${MYSQL_USER}
      MARIADB_PASSWORD: ${MYSQL_PASSWORD}
volumes:
  database-data:
```

Now start the compose.

`docker-compose up -d`
