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
import urllib

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailsearch import index
from taggit.models import TaggedItemBase, Tag
from modelcluster.contrib.taggit import  ClusterTaggableManager
from modelcluster.fields import ParentalKey
import datetime


def get_product_context(context):
    """
    Get context data on all product related pages

    :param context: the current context
    """
    context['authors'] = get_user_model().objects.filter(
        owned_pages__live=True,
        owned_pages__content_type__model='productpage'
    ).annotate(Count('owned_pages')).order_by('-owned_pages__count')
    context['all_categories'] = ProductCategory.objects.all()
    context['root_categories'] = ProductCategory.objects.filter(
        parent=None,
    ).prefetch_related(
        'children',)
    # ).annotate(
    #     product_count=Count('productpage'),
    # )
    return context


class ProductIndexPage(Page):
    @property
    def products(self):
        # Get list of product pages that are descendants of this page
        products = ProductPage.objects.descendant_of(self).live()
        products = products.order_by(
            '-date'
        ).select_related('owner').prefetch_related(
            'tagged_items__tag',
            'categories',
            'categories__category',
        )
        return products

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(ProductIndexPage, self).get_context(
            request, *args, **kwargs)
        products = self.products

        if tag is None:
            tag = request.GET.get('tag')
        if tag:
            products = products.filter(tags__slug=tag)
        if category is None:  # Not coming from category_view in views.py
            if request.GET.get('category'):
                category = get_object_or_404(
                    ProductCategory, slug=request.GET.get('category'))
        if category:
            if not request.GET.get('category'):
                category = get_object_or_404(ProductCategory, slug=category)
            products = products.filter(categories__category__name=category)
        if author:
            if isinstance(author, str) and not author.isdigit():
                products = products.filter(author__username=author)
            else:
                products = products.filter(author_id=author)

        # Pagination
        page = request.GET.get('page')
        page_size = 9
        if hasattr(settings, 'PROJECT_PAGINATION_PER_PAGE'):
            page_size = settings.PROJECT_PAGINATION_PER_PAGE

        if page_size is not None:
            paginator = Paginator(products, page_size)  # Show 10 blogs per page
            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)

        context['categories'] = ProductCategory.objects.all()
        context['number_of_products'] = ProductPage.objects.count() # Todo: update with tag
        context['products'] = products
        context['category'] = category
        context['tag'] = tag
        context['author'] = author
        context = get_product_context(context)

        return context


    class Meta:
        verbose_name = _('Products index')

    subpage_types = ['fundraiser.ProductPage']


@register_snippet
class ProductCategory(models.Model):
    name = models.CharField(
        max_length=80, unique=True, verbose_name=_('Category Name'))
    slug = models.SlugField(unique=True, max_length=80)
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name="children",
        help_text=_(
            'Categories, unlike tags, can have a hierarchy. You might have a '
            'Jazz category, and under that have children categories for Bebop'
            ' and Big Band. Totally optional.')
    )
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")

    panels = [
        FieldPanel('name'),
        FieldPanel('parent'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent:
            parent = self.parent
            if self.parent == self:
                raise ValidationError('Parent category cannot be self.')
            if parent.parent and parent.parent == self:
                raise ValidationError('Cannot have circular Parents.')

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            count = ProductCategory.objects.filter(slug=slug).count()
            if count > 0:
                slug = '{}-{}'.format(slug, count)
            self.slug = slug
        return super(ProductCategory, self).save(*args, **kwargs)


class ProductCategoryProductPage(models.Model):
    category = models.ForeignKey(
        ProductCategory, related_name="+", verbose_name=_('Category'))
    page = ParentalKey('ProductPage', related_name='categories')
    panels = [
        FieldPanel('category'),
    ]


class ProductPageTag(TaggedItemBase):
    content_object = ParentalKey('ProductPage', related_name='tagged_items')


@register_snippet
class ProductTag(Tag):
    class Meta:
        proxy = True


def product_limit_author_choices():
    """ Limit choices in product author field based on config settings """
    LIMIT_AUTHOR_CHOICES = getattr(settings, 'PROJECT_LIMIT_AUTHOR_CHOICES_GROUP', None)
    if LIMIT_AUTHOR_CHOICES:
        if isinstance(LIMIT_AUTHOR_CHOICES, str):
            limit = Q(groups__name=LIMIT_AUTHOR_CHOICES)
        else:
            limit = Q()
            for s in LIMIT_AUTHOR_CHOICES:
                limit = limit | Q(groups__name=s)
        if getattr(settings, 'PROJECT_LIMIT_AUTHOR_CHOICES_ADMIN', False):
            limit = limit | Q(is_staff=True)
    else:
        limit = {'is_staff': True}
    return limit


class ProductPage(RoutablePageMixin, Page):
    teaser = models.TextField()
    description = RichTextField(blank=True)
    organisation = models.CharField(max_length=250, blank=True)
    stock = models.PositiveIntegerField()
    prize = models.PositiveIntegerField()
    tags = ClusterTaggableManager(through=ProductPageTag, blank=True)

    date = models.DateField(
        _("Post date"), default=datetime.datetime.today,
        help_text=_("This date may be displayed on the blog post. It is not "
                    "used to schedule posts to go live at a later date.")
    )
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Header image')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        limit_choices_to=product_limit_author_choices,
        verbose_name=_('Author'),
        on_delete=models.SET_NULL,
        related_name='author_product_pages',
    )

    search_fields = Page.search_fields + (
        index.SearchField('description'),
        index.SearchField('organisation'),
    )

    settings_panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('go_live_at'),
                FieldPanel('expire_at'),
            ], classname="label-above"),
        ], 'Scheduled publishing', classname="publishing"),
        FieldPanel('date'),
        FieldPanel('author'),
    ]

    def save_revision(self, *args, **kwargs):
        if not self.author:
            self.author = self.owner
        return super(ProductPage, self).save_revision(*args, **kwargs)

    def get_absolute_url(self):
        return self.url

    def get_product_index(self):
        # Find closest ancestor which is a product index
        return self.get_ancestors().type(ProductIndexPage).last()

    def get_context(self, request, *args, **kwargs):
        context = super(ProductPage, self).get_context(request, *args, **kwargs)
        context['products'] = self.get_product_index().productindexpage.products
        context = get_product_context(context)
        return context


    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    parent_page_types = ['fundraiser.ProductIndexPage']

ProductPage.content_panels = [
    FieldPanel('title', classname="full title"),
    MultiFieldPanel([
        FieldPanel('tags'),
        InlinePanel('categories', label=_("Categories")),
    ], heading="Tags and Categories"),
    ImageChooserPanel('header_image'),
    FieldPanel('teaser', classname="full intro"),
    FieldPanel('description', classname="full"),
    FieldPanel('organisation', classname="full organisation"),
    FieldPanel('prize', classname="full prize"),
    FieldPanel('stock', classname="full stock"),
]
