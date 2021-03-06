from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from view_checks import render_bioerosion_page
import urllib
from bioerosion_search.SolrQuery import BioerosionSolrSearch, SearchType
import logging

logger = logging.getLogger(__name__)


def get_search_context(request):

    term1 = request.GET.get('term1')
    term2 = request.GET.get('term2')
    term3 = request.GET.get('term3')
    search_type = request.GET.get('st')
    journal = request.GET.get('journal')
    page = request.GET.get('page')
    csv = request.GET.get('csv')

    if term2 is None:
        term2 = ''

    if term3 is None:
        term3 = ''

    if journal is None:
        journal = ''

    a = urllib.parse.quote(journal)
    x = urllib.parse.quote(term1)
    y = urllib.parse.quote(term2)
    z = urllib.parse.quote(term3)

    csv_link_journal \
        = "/search/search-ajax-journal?term1=%s&term2=%s&term3=%s&st=%s&exp=false&csv=%s" % \
          (x, y, z, search_type, "True")

    csv_link_article \
        = "/search/search-ajax-article?term1=%s&term2=%s&term3=%s&journal=%s&st=%s&exp=false&csv=%s" % \
          (x, y, z, a, search_type, "True")

    if not page:
        page = '0'

    search_context = {'term1': term1, 'term2': term2, 'term3': term3, 'st': search_type, 'journal': journal,
                      'page': page, 'csv': csv, 'csv_link_journal': csv_link_journal,
                      'csv_link_article': csv_link_article}
    return search_context

@login_required
def index(request):
    return render_bioerosion_page(request, 'search/search.html')


@login_required
def search_ajax_journal(request):

    search_context = get_search_context(request)
    search = BioerosionSolrSearch()
    journal_results = search.query_journal(search_context, SearchType(int(search_context['st'])))
    if not search_context['csv']:
        return render_bioerosion_page(request, "search/search_ajax_journal_level.html",
                                  {'results': journal_results, 'search_context': search_context})
    else:
        return get_journal_csv_reponse(journal_results, search_context)


@login_required
def search_ajax_article(request):

    search_context = get_search_context(request)

    search = BioerosionSolrSearch()
    if not search_context['csv']:
        article_results = search.query_articles(search_context, SearchType(int(search_context['st'])), True)
        return render_bioerosion_page(request, "search/search_ajax_article_level.html",
                                  {'results_context': article_results, 'search_context': search_context})
    else:
        article_results = search.query_articles(search_context, SearchType(int(search_context['st'])), False)
        return get_article_csv_reponse(article_results, search_context)


def get_journal_csv_reponse(results, search_context):
    content = get_journal_csv(results, search_context)
    response = HttpResponse(content)
    response['content_type'] = 'text/csv'
    response['Content-Length'] = len(response.content)
    response['Content-Disposition'] = 'attachment; filename="bioerosional_journal_level_results.csv"'
    return response


def get_journal_csv(results, search_context):
    output = "\"Search Criteria\",\"Search Type\",\"Journal\",\"Number of Results\"" + '\n'
    criteria = "\"'%s','%s','%s'\"" % (search_context['term1'], search_context['term2'], search_context['term3'])
    for j in results['journals']:
        line = "%s,%s,%s,%s" % (criteria, SearchType(int(search_context['st'])).name, j, results[j]['result_count'])
        output += (line + '\n')

    return output


def get_article_csv_reponse(results, search_context):
    content = get_article_csv(results, search_context)
    response = HttpResponse(content)
    response['content_type'] = 'text/csv'
    response['Content-Length'] = len(response.content)
    response['Content-Disposition'] = 'attachment; filename="bioerosional_article_level_results.csv"'
    return response


def get_article_csv(results, search_context):
    output = "\"Search Criteria\",\"Search Type\",\"Journal\",\"Title\",\"DOI\",\"Citation\",\"Number of Incidences\"" \
             + '\n'
    criteria = "\"'%s','%s'.'%s'\"" % (search_context['term1'], search_context['term2'], search_context['term3'])
    for r in results['results']:
        line = "%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",%s" % (criteria, SearchType(int(search_context['st'])).name,
                                             r['journal'], r['title'].replace("\"", "'"), r['doi'],
                                             r['citation'].replace("<span class=\"journal-title\">", "")
                                             .replace("\"", "'")
                                             .replace("</span>", ""),
                                             results[r['journal']][r['journal_art_id']])
        output += (line + '\n')

    return output
