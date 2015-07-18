#!/usr/bin/env python

import os
from elasticsearch import Elasticsearch,helpers

ES_HOST = os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_ADDR', 'localhost' )+':'+os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_PORT', '9200' )
es = Elasticsearch([ES_HOST])
es.indices.delete(index='peticion', ignore=[400, 404])

dicts_from_file = []
with open('peticion_titulo.json','r') as inf:
    for line in inf:
        dicts_from_file.append(eval(line))

es.indices.create('peticion')
helpers.bulk(es,dicts_from_file)