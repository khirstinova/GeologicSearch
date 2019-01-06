
from django.contrib.auth.decorators import login_required
from mezzanine.pages.models import Page
from view_checks import render_geologic_page

@login_required
def home_view(request):
    page = Page.objects.filter(title="Geologic Search Home Page")
    return render_geologic_page(request, 'base_home.html', {} if page is None else {'page': page})
