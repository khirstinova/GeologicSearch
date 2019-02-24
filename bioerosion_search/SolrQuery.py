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

    journal_facet_params = {
        'facet': 'true',
        'facet.field':
        'journal_art_id',
        'facet.limit': '-1',
        'facet.mincount': '1'
    }

    def __init__(self):
        self.solr_url = "%s/%s" % (SOLR_URL, SOLR_COLLECTION)

    def query_journal(self, query, search_type):

        s = solr.SolrConnection(self.solr_url)

        try:
            response = self.journal_func_map[search_type.name](self, s, query)
            return self.process_journal_results(response)
        except KeyError:
            return None

    def query_journal_normal(self, conn, query):

        s_query = 'text:"%s"' % query['term1']
        if 'term2' in query and query['term2']:
            s_query += (' AND text:"%s"' % query['term2'])

        if 'term3' in query and query['term3']:
            s_query += (' AND text:"%s"' % query['term3'])

        return conn.query(s_query, **self.journal_facet_params)

    def query_journal_adjacent(self, conn, query):

        s_query = self.get_proximity_queries(query, '3')
        return conn.query(s_query, **self.journal_facet_params)

    def query_journal_sentence(self, conn, query):

        s_query = self.get_proximity_queries(query, '20')
        return conn.query(s_query, **self.journal_facet_params)

    def query_journal_paragraph(self, conn, query):

        s_query = self.get_proximity_queries(query, '150')
        return conn.query(s_query, **self.journal_facet_params)

    def get_proximity_queries(self, query, proximity):

        if 'term3' not in query or not query['term3']:
            if 'term2' not in query or not query['term2']:
                # Perform normal single query
                s_query = 'text:"%s"' % query['term1']
            else:
                s_query = 'text: "(\\"%s\\")(\\"%s\\")"~%s' % (query['term1'], query['term2'], proximity)
        else:
            s_query = 'text: "(\\"%s\\")(\\"%s\\")(\\"%s\\")"~%s' % \
                      (query['term1'], query['term2'], query['term3'], proximity)

        return s_query

    def process_journal_results(self, response):
        results = response.facet_counts

        return_val = defaultdict()
        return_val["journals"] = []
        return_val["journal_count"] = 0
        return_val["unique_result_count"] = 0

        collection = results['facet_fields']['journal_art_id']

        for key, value in collection.items():
            if value > 0:
                return_val["unique_result_count"] += 1

                values = key.split('---')
                journal = values[0]
                art_id = values[1]
                if journal not in return_val["journals"]:
                    return_val["journals"].append(journal)
                    return_val[journal] = {"result_count": 1, "titles": defaultdict()}
                    return_val["journal_count"] += 1
                    return_val[journal][art_id] = value
                else:
                    if art_id not in return_val[journal]["titles"]:
                        return_val[journal]["result_count"] += 1
                        return_val[journal]["titles"][art_id] = value
                    else:
                        return_val[journal]["titles"][art_id] = value

        return return_val

    def query_articles(self, query, search_type):

        s = solr.SolrConnection(self.solr_url)

        try:
            response = self.article_func_map[search_type.name](self, s, query)
            return self.process_article_results(response.results)
        except KeyError:
            return None

    def query_articles_normal(self, conn, query):

        s_query = 'text:"%s"' % query['term1']
        if 'term2' in query and query['term2']:
            s_query += (' AND text:"%s"' % query['term2'])

        if 'term3' in query and query['term3']:
            s_query += (' AND text:"%s"' % query['term3'])

        s_query = '%s AND journal:"%s"' % (s_query, query['journal'])
        return conn.query(s_query)

    def query_articles_adjacent(self, conn, query):

        s_query = self.get_proximity_queries(query, '3')
        s_query = '%s AND journal:%s' % (s_query, query['journal'])
        return conn.query(s_query)

    def query_articles_sentence(self, conn, query):

        s_query = self.get_proximity_queries(query, '20')
        s_query = '%s AND journal:%s' % (s_query, query['journal'])
        return conn.query(s_query)

    def query_articles_paragraph(self, conn, query):

        s_query = self.get_proximity_queries(query, '1500')
        s_query = '%s AND journal:%s' % (s_query, query['journal'])
        return conn.query(s_query)

    def process_article_results(self, results):
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

    journal_func_map = {
        'NORMAL': query_journal_normal,
        'ADJACENT': query_journal_adjacent,
        'SENTENCE': query_journal_sentence,
        'PARAGRAPH': query_journal_paragraph
    }

    article_func_map = {
        'NORMAL': query_articles_normal,
        'ADJACENT': query_articles_adjacent,
        'SENTENCE': query_articles_sentence,
        'PARAGRAPH': query_articles_paragraph
    }
