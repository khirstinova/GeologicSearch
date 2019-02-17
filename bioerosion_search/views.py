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
def search_ajax(request):

    term1 = request.GET.get('term1')
    search_type = request.GET.get('st')
    search = BioerosionSolrSearch()
    response = search.query(term1, SearchType(int(search_type)))
    return JsonResponse(response, safe=False)
