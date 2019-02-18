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
    search_type = request.GET.get('st')
    search = BioerosionSolrSearch()
    journal_results = search.query_journal(term1, SearchType(int(search_type)))
    return render_bioerosion_page(request, "search/search_ajax_journal_level.html", {'results': journal_results})
