from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from view_checks import render_bioerosion_page
from bioerosion_search.SolrQuery import BioerosionSolrSearch, SearchType
import logging

logger = logging.getLogger(__name__)


@login_required
def index(request):
    return render_bioerosion_page(request, 'search/search.html')


@login_required
def search_ajax_journal(request):

    term1 = request.GET.get('term1')
    term2 = request.GET.get('term2')
    term3 = request.GET.get('term3')
    search_type = request.GET.get('st')

    search_context = {'term1': term1, 'term2': term2, 'term3': term3, 'st': search_type}

    search = BioerosionSolrSearch()
    journal_results = search.query_journal(search_context, SearchType(int(search_type)))
    return render_bioerosion_page(request, "search/search_ajax_journal_level.html",
                                  {'results': journal_results, 'search_context': search_context})


@login_required
def search_ajax_article(request):

    journal = request.GET.get('journal')
    term1 = request.GET.get('term1')
    term2 = request.GET.get('term2')
    term3 = request.GET.get('term3')
    search_type = request.GET.get('st')

    search_context = {'term1': term1, 'term2': term2, 'term3': term3, 'st': search_type}

    search = BioerosionSolrSearch()
    article_results = search.query_articles(journal, search_context, SearchType(int(search_type)))
    return render_bioerosion_page(request, "search/search_ajax_article_level.html",
                                  {'results_context': article_results, 'search_context': search_context})
