from django.contrib.auth.decorators import login_required
from view_checks import render_bioerosion_page
import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    return render_bioerosion_page(request, 'search/search.html')
