"""
Fundraiser helper module
"""
from django import template
from ..models import ProductCategory, ProjectCategory

register = template.Library()

def show_product_feeds():
    """
    Return all product categories

    :return: QuerySet containing the product categories
    """
    product_categories = ProductCategory.objects.all()
    return {'categories': product_categories}

def show_project_feeds():
    """
    Return all project categories

    :return: QuerySet containing the project categories
    """
    project_categories = ProjectCategory.objects.all()
    return {'categories': project_categories}

register.inclusion_tag('fundraiser/templatetags/show_product_feeds.html')(show_product_feeds)
register.inclusion_tag('fundraiser/templatetags/show_project_feeds.html')(show_project_feeds)
