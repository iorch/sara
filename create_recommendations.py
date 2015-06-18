from elasticsearch import Elasticsearch,helpers
es = Elasticsearch()

dicts_from_file = []
with open('peticion_titulo.json','r') as inf:
    for line in inf:
        dicts_from_file.append(eval(line))

es.indices.create('peticion')
helpers.bulk(es,dicts_from_file)