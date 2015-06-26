# SARA

_Un sistema automático de atención a ciudadanos_

[![Stories in Ready](https://badge.waffle.io/mxabierto/sara.png?label=ready&title=Ready)](https://waffle.io/mxabierto/sara)

![SARA OS](http://www.rapportoconfidenziale.org/wp-content/uploads/2014/04/hergif.gif)

En este repositorio, se encuentra un código que genera un modelo de Random Forest que clasifica las peticiones recibidas en el portal de atención ciudadana, con respecto a la Dependencia gubernamental que debería atenderla.
Además, contiene un servicio web que recibe la petición en fromato json y responde con la dependencia asignada por el clasificador.

## Instrucciones de uso
__Elastic Search__
```sh
docker run \
--name sara-es \
-P -d elasticsearch 
```

__MySQL__
```sh
docker run \
--name sara-mysql \
-e MYSQL_ROOT_PASSWORD=root \
-v /SOME/VALID/PATH:/var/lib/mysql \
-P -d mysql
```

__Redis__
```sh
docker run \
--name sara-redis \
-v /OTHER/VALID/PATH:/data \
-P -d redis
```

__SARA__
```sh
docker run \
-v `pwd`/logs:/logs \
--name sara \
--link sara-mysql:mysql \
--link sara-es:elasticsearch \
--link sara-redis:redis \
-e PETITIONS_SERVER_URL="x.x.x.x" \
-p 5000:5000 \
-d mxabierto/sara
```