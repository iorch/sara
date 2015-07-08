# SARA

_Un sistema automático de atención a ciudadanos_

[![Stories in Ready](https://badge.waffle.io/mxabierto/sara.png?label=ready&title=Ready)](https://waffle.io/mxabierto/sara)

![SARA OS](http://www.rapportoconfidenziale.org/wp-content/uploads/2014/04/hergif.gif)

En este repositorio, se encuentra un código que genera un modelo de Random Forest que clasifica las peticiones recibidas en el portal de atención ciudadana, con respecto a la Dependencia gubernamental que debería atenderla.
Además, contiene un servicio web que recibe la petición en fromato json y responde con la dependencia asignada por el clasificador.

## Instrucciones de uso

Ejecución del servicio:

```
fleetctl load services/*.service
fleetctl start sara.service
```

Inspeccionar logs de cualquier componente:

```
fleetctl journal -f sara
```

Detener el servicio:

```
fleetctl stop sara
```