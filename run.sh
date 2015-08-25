#!/usr/bin/env bash
# boot2docker down
# boot2docker --vbox-share=<data_in_macos>=<data_in_boot2docker-vm> up

docker run \
--name sara_mysql \
-v <data_in_boot2docker-vm>/mysql:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=root \
-P -d mysql

docker run \
--name sara_redis \
-v <data_in_boot2docker-vm>/redis:/data \
-P -d redis

docker run \
--name sara_elasticsearch \
-P -d elasticsearch

docker run \
-v <data_in_boot2docker-vm>/logs:/logs \
-v <data_in_boot2docker-vm>/db:/tmp/ \
--name sara_app \
--link sara_mysql:mysql \
--link sara_elasticsearch:elasticsearch \
--link sara_redis:redis \
-e PETITIONS_SERVER_URL="http://www.myurl.com/update" \
-e SARA_MODEL="https://s3.amazonaws.com/org.mxabierto/sara/model-0.1.tgz" \
-e DEBUG_MODE=False \
-e SQLALCHEMY_URL=sqlite:////tmp/users.db \
-e SECRET_KEY="passwd" \
-p 5000:5000 \
-d mxabierto/sara
