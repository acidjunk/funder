from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^search/', views.search, name="search"),
    url(r'^project-tag/(?P<tag>[-\w]+)/', views.project_tag_view, name="project_tag"),
    url(r'^product-tag/(?P<tag>[-\w]+)/', views.product_tag_view, name="product_tag"),

    url(r'^project-category/(?P<category>[-\w]+)/feed/$', views.ProjectLatestCategoryFeed(), name="project_category_feed"),
    url(r'^project-category/(?P<category>[-\w]+)/', views.project_category_view, name="project_category"),
    url(r'^product-category/(?P<category>[-\w]+)/feed/$', views.ProductLatestCategoryFeed(),
        name="product_category_feed"),
    url(r'^product-category/(?P<category>[-\w]+)/', views.product_category_view, name="product_category"),

    url(r'^author/(?P<author>[-\w]+)/', views.author_view, name="author"),

    url(r'(?P<project_slug>[\w-]+)/rss.*/',
        views.ProjectLatestEntriesFeed(),
        name="project_latest_entries_feed"),
    url(r'(?P<project_slug>[\w-]+)/atom.*/',
        views.ProjectLatestEntriesFeedAtom(),
        name="project_latest_entries_feed_atom"),
    url(r'(?P<product_slug>[\w-]+)/rss.*/',
        views.ProductLatestEntriesFeed(),
        name="product_latest_entries_feed"),
    url(r'(?P<product_slug>[\w-]+)/atom.*/',
        views.ProductLatestEntriesFeedAtom(),
        name="product_latest_entries_feed_atom"),
]
