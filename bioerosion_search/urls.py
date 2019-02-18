#the product app urls page
from django.conf.urls import url
from bioerosion_search import views

urlpatterns = [

    # ex: /products/
    url(r'^$', views.index, name='index'),
    url(r'^search-ajax-journal$', views.search_ajax_journal, name='search_ajax_journal'),
    url(r'^search-ajax-article$', views.search_ajax_article, name='search_ajax_article'),
]
