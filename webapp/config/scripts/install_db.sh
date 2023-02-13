#!/bin/ash
DATE=`date '+%Y-%m-%d %H:%m:%S'`

if [[ -z "$MYSQL_USER" ]]
then
	USER="piglet"
else
	USER="${MYSQL_USER}"
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

while ! nc -z database 3306 &> /dev/null
do
	echo "$DATE waiting for database host"
	sleep 5
done

TABLES=`mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST -e 'show tables'`

if [ -z "$TABLES" ]
then
	echo "$DATE Import schema"
	mysql -u $USER -p$MYSQL_PASSWORD $DATABASE -h $HOST < /webapp/config/scripts/piglet-schema.sql
	exit 0
else
	echo "$DATE Database schema is already set - not overwriting"
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
	

