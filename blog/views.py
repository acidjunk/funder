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
from django.utils.feedgenerator import Atom1Feed
from .models import BlogIndexPage, BlogPage, BlogCategory
from django.shortcuts import get_object_or_404, render
from django.conf import settings

from wagtail.wagtailsearch.models import Query

def tag_view(request, tag):
    index = BlogIndexPage.objects.first()
    return index.serve(request, tag=tag)


def category_view(request, category):
    index = BlogIndexPage.objects.first()
    return index.serve(request, category=category)


def author_view(request, author):
    index = BlogIndexPage.objects.first()
    return index.serve(request, author=author)

def search(request):
    # Search
    search_query = request.GET.get('query', None)
    if search_query:
        search_results = BlogPage.objects.live().search(search_query)
        print search_results

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = BlogPage.objects.none()

    # Render template
    return render(request, 'blog/search_results.html', {
        'search_query': search_query,
        'search_results': search_results,
    })

class LatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching BlogIndexPage
    and return its items.
    '''

    def get_object(self, request, blog_slug):
        return get_object_or_404(BlogIndexPage, slug=blog_slug)

    def title(self, blog):
        if blog.seo_title:
            return blog.seo_title
        return blog.title

    def link(self, blog):
        return blog.full_url

    def description(self, blog):
        return blog.search_description

    def items(self, blog):
        num = getattr(settings, 'BLOG_PAGINATION_PER_PAGE', 10)
        return blog.get_descendants()[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.specific.body

    def item_link(self, item):
        return item.full_url


class LatestEntriesFeedAtom(LatestEntriesFeed):
    feed_type = Atom1Feed


class LatestCategoryFeed(Feed):
    description = "A Blog"

    def title(self, category):
        return "Blog: " + category.name

    def link(self, category):
        return "/blog/category/" + category.slug

    def get_object(self, request, category):
        return get_object_or_404(BlogCategory, slug=category)

    def items(self, obj):
        return BlogPage.objects.filter(
            categories__category=obj).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body