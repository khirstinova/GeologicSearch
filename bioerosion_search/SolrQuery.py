import solr
from config.settings import SOLR_COLLECTION, SOLR_URL
from enum import Enum


class SearchType(Enum):
    NORMAL = 1
    ADJACENT = 2
    SENTENCE = 3
    PARAGRAPH = 4


class BioerosionSolrSearch:

    def __init__(self):
        self.solr_url = "%s/%s" % (SOLR_URL, SOLR_COLLECTION)


    def query(self, query, search_type):
        if search_type == SearchType.NORMAL:
            return self.query_normal(query)

        return None

    def query_normal(self, query):
        s = solr.SolrConnection(self.solr_url)
        # select = s.SearchHandler(s, "/collection1/select")
        response = s.query('text:%s' % query)
        return response.results
