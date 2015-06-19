# SARA

_Un sistema automático de atención a ciudadanos_

[![Stories in Ready](https://badge.waffle.io/mxabierto/sara.png?label=ready&title=Ready)](https://waffle.io/mxabierto/sara)

![SARA OS](http://www.rapportoconfidenziale.org/wp-content/uploads/2014/04/hergif.gif)

En este repositorio, se encuentra un código que genera un modelo de Random Forest que clasifica las peticiones recibidas en el portal de atención ciudadana, con respecto a la Dependencia gubernamental que debería atenderla.
Además, contiene un servicio web que recibe la petición en fromato json y responde con la dependencia asignada por el clasificador.

## Instrucciones de uso
1. Se asume que se tiene aislado el ambiente de python, con todos los requerimientos listados en requirement.txt
2. Crear las carpetas data/, plots/, models/
3. Ejecutar BagOfWords.py
4. Iniciar redis-server y `celery -A tasks worker --loglevel=info`
5. Encender el servicio web:  ml_classifier.py

## Docker
Para utilizar el app en contenedores basta ejecutar sus componentes individuales:

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
-d redis
```

__SARA__
```sh
docker run \
--name sara \
--link sara-mysql:mysql \
--link sara-es:elasticsearch \
--link sara-redis:redis \
-p 5000:5000 \
-d mxabierto/sara
```