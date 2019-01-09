
from django.contrib.auth.decorators import login_required
from mezzanine.accounts.views import login as builtin_login
from mezzanine.pages.models import Page
from view_checks import render_bioerosion_page

@login_required
def home_view(request):
    page = Page.objects.filter(title="Geologic Search Home Page")
    return render_bioerosion_page(request, 'base_home.html', {} if page is None else {'page': page})

def login(request, *args, **kwargs):
    response = builtin_login(request, *args, **kwargs)
    # Basically, this checks whether the form had errors.  If it did, it tries the form again with a
    # lowercase username.  If it fails at that point, it's a definite failure.
    if request.method == 'POST' and hasattr(response, 'context_data') and not \
            (response.context_data['form'].is_bound and not bool(response.context_data['form']._errors)):
        request.POST._mutable = True
        request.POST['username'] = request.POST['username'].lower()
        request.POST._mutable = False
        response = builtin_login(request, *args, **kwargs)
    return response
