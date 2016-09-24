"""
Blog helper module
"""
from django import template
from ..models import BlogCategory

register = template.Library()


def show_blog_feeds():
    """
    Return all blog categories

    :return: QuerySet containing the blog categories
    """
    blog_categories = BlogCategory.objects.all()
    return {'categories': blog_categories}

register.inclusion_tag('blog/templatetags/show_blog_feeds.html')(show_blog_feeds)
