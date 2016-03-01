#!/usr/bin/env bash

docker stop mysql
docker rm mysql
docker run --name mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=True -e MYSQL_DATABASE=sacdb -d mysql
docker cp /Users/iorch/mxabierto/DATA/SAC/dumpSAC.sql mysql:/dumpSAC.sql
docker exec -i mysql bash -c 'exec mysql -uroot -hlocalhost sacdb < /dumpSAC.sql'
docker build -t model .
docker run -it --link mysql:model model bash -c 'cd sara && python trainer.py'
