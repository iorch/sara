#!/usr/bin/env python

import os
from elasticsearch import Elasticsearch,helpers

ES_HOST = os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_ADDR', 'localhost' )+':'+os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_PORT', '9200' )
es = Elasticsearch([ES_HOST])
es.indices.delete(index='peticion', ignore=[400, 404])
null = None

index_names = [
    {'name': 'peticion', 'file': 'peticion_titulo.json'},
    {'name': 'formalities', 'file': 'formalities.json'}
    ]
dicts = {}
for index in index_names:
    index_name = index['name']
    dicts[index_name] = []
    f = index['file']
    with open(f,'r') as inf:
        for line in inf:
            dicts[index_name].append(eval(line))
    es.indices.create(index_name)
    helpers.bulk(es,dicts[index_name])
