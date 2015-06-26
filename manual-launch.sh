#!/bin/bash
# This is a nasty and temporary solution to launch the service in a somehow
# replicable-and-portable way; should be replaced with a formal service
# definition ASAP

# Create data dirs
if [ ! -d 'data' ]; then
  mkdir data
fi
if [ ! -d 'redis' ]; then
  mkdir redis
fi
if [ ! -d 'logs' ]; then
  mkdir logs
fi

# Start base dependencies
echo "Starting: MySQL"
docker run --name sara-mysql -v `pwd`/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=root -P -d mysql

echo "Starting: Elastic Search"
docker run --name sara-es -P -d elasticsearch

echo "Starting: Redis"
docker run --name sara-redis -v `pwd`/redis:/data -P -d redis

# Populate database if a dump file is present
if [ -d 'sacdb-data' ]; then
  # Wait for mysql server to become fully operational the lazy way =/
  sleep 15
  
  # Load dump file into server container
  echo "Loading dump data..."
  docker run -it --rm \
  --link sara-mysql:mysql \
  -v `pwd`/sacdb-data:/dump \
  mysql \
  sh -c 'exec mysql -h"$MYSQL_PORT_3306_TCP_ADDR" -P"$MYSQL_PORT_3306_TCP_PORT" -uroot -p"$MYSQL_ENV_MYSQL_ROOT_PASSWORD" < /dump/dump.sql'
fi

# Start service
echo "Starting SARA"
docker run \
-v `pwd`/logs:/logs \
--name sara \
--link sara-mysql:mysql \
--link sara-es:elasticsearch \
--link sara-redis:redis \
-e PETITIONS_SERVER_URL="http://www.gob.mx/SAC/petitionClassifier/update" \
-p 5000:5000 \
-d mxabierto/sara