#!/bin/ash

if [[ -z "$MYSQL_USER" ]];
then
	USER="${MYSQL_USER}"
else
	USER="piglet"
fi

if [[ -z "$MYSQL_HOST" ]];
then
	HOST="${MYSQL_HOST}"
else
	HOST="piglet"
fi

if [[ -z "$MYSQL_DATABASE" ]];
then
	DATABASE="${MYSQL_DATABASE}"
else
	DATABASE="piglet"
fi

while ! nc -z database 3306 &> /dev/null
do
	echo "waiting for database host"
	sleep 5
done


TABLES=`mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST -e 'show tables'`

if [ -z "$TABLES" ]
then
	echo "Import schema"
	mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST < /opt/scripts/piglet-schema.sql
	exit 0
else
	echo "Database schema is already set - not overwriting"
	exit 0
fi
	
#DATA=`mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -h database -e 'select id from registered_user where id=1'`
#echo $DATA
#if [ -f "/var/lib/mysql/installed"  ]
#then
#	echo "Database already initialized"
#else
#	mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE < /opt/scripts/piglet.sql
#	touch "/var/lib/mysql/installed"
#fi
	

