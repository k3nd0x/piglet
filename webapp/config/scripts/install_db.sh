#!/bin/ash

sleep 1
DATE=`date '+%Y-%m-%d %H:%m:%S'`

if [[ -z "$MYSQL_USER" ]]
then
	USER="piglet"
else
	USER="${MYSQL_USER}"
fi

if [[ -z "$MYSQL_PORT" ]]
then
	PORT="3306"
else
	PORT="${MYSQL_PORT}"
fi

if [[ -z "$MYSQL_HOST" ]]
then
	HOST="database"
else
	HOST="${MYSQL_HOST}"
fi

if [[ -z "$MYSQL_DATABASE" ]]
then
	DATABASE="piglet"
else
	DATABASE="${MYSQL_DATABASE}"
fi

while ! nc -z $HOST $PORT &> /dev/null
do
	echo "$DATE waiting for database host"
	sleep 5
done

if [[ -z "${DB_ROOT_PASSWORD}" ]]
then
	echo "$DATE You have to create your own user and database if MYSQL_ROOT_PASSWORD is not provided"
	exit 0
else
	echo "$DATE create database $DATABASE if not exist"
	mysql -u root -p"$DB_ROOT_PASSWORD" -h "$HOST" -e "create database IF NOT EXISTS $DATABASE"
	if [[ $? != 0 ]]
	then
		echo "$DATE provided root password is not correct"
		exit 128
	fi
	mysql -u root -p"$DB_ROOT_PASSWORD" -h "$HOST" -e "create user IF NOT EXISTS '$USER'@'%' identified by '$MYSQL_PASSWORD'"
	mysql -u root -p"$DB_ROOT_PASSWORD" -h "$HOST" -e "grant all privileges on $DATABASE.* to $USER@'%'"
fi

TABLES=`mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST -e 'show tables'`

if [ -z "$TABLES" ]
then
	echo "$DATE Import schema"
	mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST < /webapp/config/dbschema/init/piglet-schema.sql
	exit 0
else
	echo "$DATE Database schema is already set - not overwriting"
	exit 0
fi