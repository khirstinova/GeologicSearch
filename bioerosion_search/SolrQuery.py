import solr
from config.settings import SOLR_COLLECTION, SOLR_URL
from collections import defaultdict
from enum import Enum


class SearchType(Enum):
    NORMAL = 1
    ADJACENT = 2
    SENTENCE = 3
    PARAGRAPH = 4


class BioerosionSolrSearch:

    def __init__(self):
        self.solr_url = "%s/%s" % (SOLR_URL, SOLR_COLLECTION)


    def query_journal(self, query, search_type):
        if search_type == SearchType.NORMAL:
            return self.query_normal_journal(query)

        return None

    def query_normal_journal(self, query):
        s = solr.SolrConnection(self.solr_url)
        # select = s.SearchHandler(s, "/collection1/select")
        response = s.query('text:%s' % query)
        results = response.results
        return_val = defaultdict()
        return_val["journals"] = []

        for r in results:
            journal = r["journal"][0]
            if journal not in return_val["journals"]:
                return_val["journals"].append(journal)
                return_val[journal] = 1
            else:
                return_val[journal] += 1

        return return_val
