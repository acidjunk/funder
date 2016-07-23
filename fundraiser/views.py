from django.contrib.syndication.views import Feed
from django.views.generic import TemplateView
from django.utils.feedgenerator import Atom1Feed
from .models import ProjectIndexPage, ProjectPage, ProjectCategory
from django.shortcuts import get_object_or_404
from django.conf import settings


def tag_view(request, tag):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, tag=tag)


def category_view(request, category):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, category=category)


def author_view(request, author):
    index = ProjectIndexPage.objects.first()
    return index.serve(request, author=author)


class LatestEntriesFeed(Feed):
    '''
    If a URL ends with "rss" try to find a matching BlogIndexPage
    and return its items.
    '''

    def get_object(self, request, blog_slug):
        return get_object_or_404(ProjectIndexPage, slug=blog_slug)

    def title(self, blog):
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


class LatestEntriesFeedAtom(LatestEntriesFeed):
    feed_type = Atom1Feed


class LatestCategoryFeed(Feed):
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
