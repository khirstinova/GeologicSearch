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
        response = s.query('text:%s' % query)
        results = response.results
        return_val = defaultdict()
        return_val["journals"] = []
        return_val["journal_count"] = 0
        return_val["unique_result_count"] = 0

        for r in results:
            journal = r["journal"][0]
            title = r["title"][0]
            if journal not in return_val["journals"]:
                return_val["journals"].append(journal)
                return_val[journal] = {"result_count": 1, "titles": defaultdict()}
                return_val["journal_count"] += 1
                return_val[journal][title] = 1
                return_val["unique_result_count"] += 1
            else:
                if title not in return_val[journal]["titles"]:
                    return_val[journal]["result_count"] += 1
                    return_val[journal]["titles"][title] = 1
                    return_val["unique_result_count"] += 1
                else:
                    return_val[journal]["titles"][title] += 1

        return return_val

    def query_articles(self, journal, query, search_type):
        if search_type == SearchType.NORMAL:
            return self.query_normal_articles(journal, query)

        return None

    def query_normal_articles(self, journal, query):
        s = solr.SolrConnection(self.solr_url)
        response = s.query('text:%s AND journal:%s' % (query, journal))
        results = response.results
        return_val = defaultdict()
        return_val['results'] = []

        for r in results:
            result = defaultdict()

            journal = r['journal'][0]
            title = r["title"][0]

            if journal not in return_val:
                return_val[journal] = defaultdict()

            if title not in return_val[journal]:
                return_val[journal][title] = 1
                result['journal'] = journal
                result['title'] = title
                result['doi'] = r['doi']
                result['citation'] = r['citation'][0]
                return_val['results'].append(result)
            else:
                return_val[journal][title] += 1

        return return_val
