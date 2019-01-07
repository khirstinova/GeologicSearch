from django.contrib.auth.decorators import login_required
from view_checks import render_geologic_page
import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    return render_geologic_page(request, 'base_home.html')
