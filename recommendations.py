#!/usr/bin/env python
# coding=utf-8

import os
from elasticsearch import Elasticsearch,helpers
import pprint


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        _escape = dict((q, dict((c, unicode(repr(chr(c)))[1:-1])
                                    for c in range(32) + [ord('\\')] +
                                    range(128, 161),
                                    **{ord(q): u'\\' + q}))
                           for q in ["'", '"'])
        if type(object) is unicode:
            q = "'" if "'" not in object or '"' in object \
                else '"'
            return ("u" + q + object.translate(_escape[q]) +
                    q, True, False)
        return pprint.PrettyPrinter.format(
            self, object, context, maxlevels, level)

class Recommender:
    def __init__(self):
        self.ES_HOST = os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_ADDR', 'localhost' ) \
            + ':' + os.getenv( 'ELASTICSEARCH_PORT_9200_TCP_PORT', '9200' )
        self.es = Elasticsearch( [self.ES_HOST] )
        self.index_config = {
            'peticion': {'file': 'peticion_titulo.json',
                        'type': 'pregunta',
                        'fields':["titulo", "keywords"],
                        'links': 'links',
                        'titulo': 'titulo',
                        'sugerencia': 'sugerencia',
                        'page_rank': None},
            'formalities': { 'file': 'formalities.json',
                        'type': 'tramite',
                        'fields': ['process_citizen_name','description_citizen'],
                        'links': 'process_online_link',
                        'titulo': 'process_citizen_name',
                        'sugerencia': 'description_citizen',
                        'page_rank': None},
            'page_rank': {'file': 'recommendations.json',
                        'type': 'ranked_search',
                        'fields': ['content', 'title'],
                        'links': 'link',
                        'titulo': 'title',
                        'sugerencia': 'content',
                        'page_rank': 'score'},
            }


    def delete_index(self, index_name = ''):
        self.es.indices.delete( index = index_name, ignore = [400, 404] )

    def create_recommendations(self):
        null = None
        dicts = {}
        for index in self.index_config:
            index_name = index
            dicts[index_name] = []
            f = self.index_config[index]['file']
            with open(f,'r') as inf:
                for line in inf:
                    dicts[index_name].append(eval(line))
            self.es.indices.create(index_name)
            helpers.bulk(self.es,dicts[index_name])

    def get_links(self, links):
        clean_links = []
        if links.__class__.__name__ == 'NoneType':
            return clean_links
        #Make sure that link starts with a http protocol
        for link in links:
            try:
                 link[:4]==u"http"
            except TypeError:
                link = link[u'link']
            if (link[:7]==u"http://" or link[:8]==u"https://"):
                clean_links.append(link)
            else:
                clean_links.append(u"http://"+link)
        return clean_links

    def get_relevant_hits(self, like_text, index_name):
        doc_type = self.index_config[index_name]['type']
        stop_words = ["a", "quiero", "para", "apoyo", "una", "la", "el", "de", \
            "del", "en", "solicito", "solicitud", "programa"]
        body = { "query": {
                    "more_like_this": {
                        "fields": self.index_config[index_name]['fields'],
                        "like_text": like_text, "min_term_freq": 1,
                        "max_query_terms": 100, "min_doc_freq": 0,
                        "stop_words": stop_words }
                        }
        }
        mlts = self.es.search(index=index_name, doc_type=doc_type, body=body)
        relevant_sugestions = []
        hits = mlts.get('hits')["hits"]
        for hit in hits:
            if hit["_score"] >= 0.3:
                source = hit["_source"]
                links = self.get_links(source[self.index_config[index_name]['links']])
                titulo = source[self.index_config[index_name]['titulo']]
                sugerencia = source[self.index_config[index_name]['sugerencia']]
                page_rank_name = self.index_config[index_name]['page_rank']
                if page_rank_name:
                    page_rank = source[page_rank_name]
                else:
                    page_rank = None
                relevant_sugestions.append({u"title": unicode(titulo),
                                            u"description": unicode(sugerencia),
                                            u"links": links,
                                            u'page_rank': page_rank,
                                            u"score": hit["_score"]})
        return relevant_sugestions


if __name__ == '__main__':
    pp = MyPrettyPrinter()
    r = Recommender()
    r.create_recommendations()
    pp.pprint(r.get_relevant_hits("trabajo",'formalities'))
    pp.pprint(r.get_relevant_hits("trabajo",'peticion'))
