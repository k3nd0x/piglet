# piglet :pig:

Simple Webapp to manage and administrate budgets in a household

# About

This project is an easy webapp to manage your budget. It comes with an lightweight webinterface and an api.
You can easily add, categorize and compare your expenditures, individualize your categories and profile.

# Installation
## With Docker
The Image is available at `k3nd0x/piglet` 

```
version: '3.3'
services:
    piglet:
      restart: unless-stopped
      container_name: piglet
      depends_on:
        - database
      ports:
        - '0.0.0.0:80:80' # Piglet
        - '0.0.0.0:8080:8080' # API
      image: piglet:1.0.1
      environment:
        MYSQL_DATABASE: ${MYSQL_DATABASE} # Default 'piglet'
        MYSQL_USER: ${MYSQL_USER} # Default 'piglet'
        MYSQL_PASSWORD: ${MYSQL_PASSWORD}
        MYSQL_HOST: ${MYSQL_HOST}
        MAIL_SERVER: ${MAIL_SERVER}
        MAIL_USER: ${MAIL_USER}
        MAIL_PASSWORD: ${MAIL_PASSWORD}
        MAIL_PORT: ${MAIL_PORT}
        MAIL_ENCRYPTIONPROTOCOL: ${MAIL_ENCRYPTIONPROTOCOL}
        DOMAIN: ${DOMAIN}
      volumes:
        - "/etc/timezone:/etc/timezone:ro"
        - "/etc/localtime:/etc/localtime:ro"
    database:
      image: mariadb:latest
      container_name: piglet-db
      volumes:
        - database-data:/var/lib/mysql
      environment:
        MYSQL_RANDOM_ROOT_PASSWORD: 1
        MYSQL_DATABASE: ${MYSQL_DATABASE}
        MYSQL_USER: ${MYSQL_USER}
        MYSQL_PASSWORD: ${MYSQL_PASSWORD}
volumes:
  database-data:
```

You can use the docker-compose.yml to create both containers (piglet, mariadb). 

Following ENV variables are possible:
| ENV variable  | description | defaults | required |
| -- | -- | -- | -- |
| MYSQL_USER  | User for the piglet database | piglet | :x:
| MYSQL_DATABASE  | Name of the piglet database | piglet | :x:
| MYSQL_HOST | Hostname or IP Address of the databasehost | database | :x:
| MYSQL_PASSWORD | Password for the piglet database user | None | :white_check_mark:
| DOMAIN | Default domain of the piglet instance | None | :x:
| MAIL_SERVER | Mailserver for email notification | None | :x:
| MAIL_PORT | Mailserver Port | None | :x:
| MAIL_USER | Mailserver User | None | :x:
| MAIL_PASSWORD | Mailserver Password | None | :x:
| MAIL_ENCRYPTIONPROTOCOL | Mailserver Encryption Protocol | None | :x:
*The Mail sending process is currently in beta state

To start the app just execute the docker-compose.yml 
```
docker-compose up
```

# Roadmap
- support for different languages
- few admin settings in the webui (e.g. mailserver config)
- html/css mobile friendly
- add some more features to reports

# Known issues
- Site is flashing white at reload when darkmode is active
- Nav Menue is popping out at reload when its in mini mode

# Disclaimer

I started to build this project at the beginning of my programming career so please be gentle if something is not working as expected.
Feel free to edit or just open a issue. Feature requests can also be added at the issue tab.
