#the product app urls page
from django.conf.urls import url
from bioerosion_search import views

urlpatterns = [

    # ex: /products/
    url(r'^$', views.index, name='index'),
    url(r'^search-ajax$', views.search_ajax, name='search_ajax'),
]
