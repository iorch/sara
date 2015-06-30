from elasticsearch import Elasticsearch,helpers
es = Elasticsearch()
es.indices.delete(index='peticion', ignore=[400, 404])
dicts_from_file = []
with open('peticion_titulo.json','r') as inf:
    for line in inf:
        dicts_from_file.append(eval(line))

es.indices.create('peticion')
helpers.bulk(es,dicts_from_file)