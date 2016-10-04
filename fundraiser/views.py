"""
Funder: a Django/Wagtail based web application to facilitate online donations.
Copyright (C) 2016 R. Dohmen <acidjunk@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from django.contrib.syndication.views import Feed
from django.views.generic import TemplateView
from django.utils.feedgenerator import Atom1Feed
from .models import ProductIndexPage, ProductPage, ProjectIndexPage, ProjectPage, ProjectCategory
from django.shortcuts import get_object_or_404, render
from django.conf import settings

# Todo use: generic Page to make search accross aa couple of tables
from wagtail.wagtailcore.models import Page

from wagtail.wagtailsearch.models import Query

def project_search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = ProjectPage.objects.live().search(search_query)
        print search_results

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = ProjectPage.objects.none()

    # Render template
    return render(request, 'fundraiser/search_results.html', {
        'title': 'Project search results',
        'search_query': search_query,
        'search_results': search_results,
    })

def product_search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = ProductPage.objects.live().search(search_query)
        print search_results

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = ProductPage.objects.none()

    # Render template
    return render(request, 'fundraiser/search_results.html', {
        'title': 'Product search results',
        'search_query': search_query,
        'search_results': search_results,
    })

def project_tag_view(request, tag):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, tag=tag)

def product_tag_view(request, tag):
    index = ProductIndexPage.objects.first()
    return index.serve(request, tag=tag)

def project_category_view(request, category):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, category=category)

def product_category_view(request, category):
    index = ProductIndexPage.objects.first()
    return index.serve(request, category=category)

def author_view(request, author):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, author=author)


class ProjectLatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching ProjectIndexPage
    and return its items.
    '''

    def get_object(self, request, project_slug):
        return get_object_or_404(ProjectIndexPage, slug=project_slug)

    def title(self, project):
        if project.seo_title:
            return project.seo_title
        return project.title

    def link(self, project):
        return project.full_url

    def description(self, project):
        return project.search_description

    def items(self, project):
        num = getattr(settings, 'PROJECT_PAGINATION_PER_PAGE', 10)
        return project.get_descendants()[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.description

    def item_link(self, item):
        return item.full_url


class ProjectLatestEntriesFeedAtom(ProjectLatestEntriesFeed):
    feed_type = Atom1Feed


class ProductLatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching ProjectIndexPage
    and return its items.
    '''

    def get_object(self, request, product_slug):
        return get_object_or_404(ProductIndexPage, slug=product_slug)

    def title(self, product):
        if product.seo_title:
            return product.seo_title
        return product.title

    def link(self, product):
        return product.full_url

    def description(self, product):
        return product.search_description

    def items(self, product):
        num = getattr(settings, 'PRODUCT_PAGINATION_PER_PAGE', 10)
        return product.get_descendants()[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.description

    def item_link(self, item):
        return item.full_url


class ProductLatestEntriesFeedAtom(ProductLatestEntriesFeed):
    feed_type = Atom1Feed


class ProjectLatestCategoryFeed(Feed):
    description = "A project"

    def title(self, category):
        return "Project: " + category.name

    def link(self, category):
        return "/projects/category/" + category.slug

    def get_object(self, request, category):
        return get_object_or_404(ProjectCategory, slug=category)

    def items(self, obj):
        return ProjectPage.objects.filter(
            categories__category=obj).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description


class ProductLatestCategoryFeed(Feed):
    description = "A product"

    def title(self, category):
        return "Product: " + category.name

    def link(self, category):
        return "/product/category/" + category.slug

    def get_object(self, request, category):
        return get_object_or_404(ProjectCategory, slug=category)

    def items(self, obj):
        return ProductPage.objects.filter(
            categories__category=obj).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
