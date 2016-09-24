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


def get_project_context(context):
    """
    Get context data on all project related pages

    :param context: the current context
    """
    context['authors'] = get_user_model().objects.filter(
        owned_pages__live=True,
        owned_pages__content_type__model='projectpage'
    ).annotate(Count('owned_pages')).order_by('-owned_pages__count')
    context['all_categories'] = ProjectCategory.objects.all()
    context['root_categories'] = ProjectCategory.objects.filter(
        parent=None,
    ).prefetch_related(
        'children',)
    # ).annotate(
    #     project_count=Count('projectpage'),
    # )
    return context


class ProjectIndexPage(Page):
    @property
    def projects(self):
        # Get list of project pages that are descendants of this page
        projects = ProjectPage.objects.descendant_of(self).live()
        projects = projects.order_by(
            '-date'
        ).select_related('owner').prefetch_related(
            'tagged_items__tag',
            'categories',
            'categories__category',
        )
        return projects

    def get_context(self, request, tag=None, category=None, author=None, *args,
                    **kwargs):
        context = super(ProjectIndexPage, self).get_context(
            request, *args, **kwargs)
        projects = self.projects

        if tag is None:
            tag = request.GET.get('tag')
        if tag:
            projects = projects.filter(tags__slug=tag)
        if category is None:  # Not coming from category_view in views.py
            if request.GET.get('category'):
                category = get_object_or_404(
                    ProjectCategory, slug=request.GET.get('category'))
        if category:
            if not request.GET.get('category'):
                category = get_object_or_404(ProjectCategory, slug=category)
            projects = projects.filter(categories__category__name=category)
        if author:
            if isinstance(author, str) and not author.isdigit():
                projects = projects.filter(author__username=author)
            else:
                projects = projects.filter(author_id=author)

        # Pagination
        page = request.GET.get('page')
        page_size = 9
        if hasattr(settings, 'PROJECT_PAGINATION_PER_PAGE'):
            page_size = settings.PROJECT_PAGINATION_PER_PAGE

        if page_size is not None:
            paginator = Paginator(projects, page_size)  # Show 10 blogs per page
            try:
                projects = paginator.page(page)
            except PageNotAnInteger:
                projects = paginator.page(1)
            except EmptyPage:
                projects = paginator.page(paginator.num_pages)

        context['categories'] = ProjectCategory.objects.all()
        context['number_of_projects'] = ProjectPage.objects.count() # Todo: update with tag
        context['projects'] = projects
        context['category'] = category
        context['tag'] = tag
        context['author'] = author
        context = get_project_context(context)

        return context


    class Meta:
        verbose_name = _('Projects index')

    subpage_types = ['fundraiser.ProjectPage']


@register_snippet
class ProjectCategory(models.Model):
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
        verbose_name = _("Project Category")
        verbose_name_plural = _("Project Categories")

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
            count = ProjectCategory.objects.filter(slug=slug).count()
            if count > 0:
                slug = '{}-{}'.format(slug, count)
            self.slug = slug
        return super(ProjectCategory, self).save(*args, **kwargs)


class ProjectCategoryProjectPage(models.Model):
    category = models.ForeignKey(
        ProjectCategory, related_name="+", verbose_name=_('Category'))
    page = ParentalKey('ProjectPage', related_name='categories')
    panels = [
        FieldPanel('category'),
    ]


class ProjectPageTag(TaggedItemBase):
    content_object = ParentalKey('ProjectPage', related_name='tagged_items')


@register_snippet
class ProjectTag(Tag):
    class Meta:
        proxy = True


def project_limit_author_choices():
    """ Limit choices in project author field based on config settings """
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


class ProjectPage(RoutablePageMixin, Page):
    teaser = models.TextField()
    description = RichTextField(blank=True)
    organisation = models.CharField(max_length=250, blank=True)
    amount_needed = models.IntegerField()
    amount_raised = models.IntegerField(default=0)
    show_comments = models.BooleanField(default=True)
    tags = ClusterTaggableManager(through=ProjectPageTag, blank=True)

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
        limit_choices_to=project_limit_author_choices,
        verbose_name=_('Author'),
        on_delete=models.SET_NULL,
        related_name='author_project_pages',
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
        return super(ProjectPage, self).save_revision(*args, **kwargs)

    def get_absolute_url(self):
        return self.url

    def get_project_index(self):
        # Find closest ancestor which is a project index
        return self.get_ancestors().type(ProjectIndexPage).last()

    def get_context(self, request, *args, **kwargs):
        context = super(ProjectPage, self).get_context(request, *args, **kwargs)
        context['projects'] = self.get_project_index().projectindexpage.projects
        context = get_project_context(context)
        return context


    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    parent_page_types = ['fundraiser.ProjectIndexPage']

ProjectPage.content_panels = [
    FieldPanel('title', classname="full title"),
    MultiFieldPanel([
        FieldPanel('tags'),
        InlinePanel('categories', label=_("Categories")),
    ], heading="Tags and Categories"),
    ImageChooserPanel('header_image'),
    FieldPanel('teaser', classname="full intro"),
    FieldPanel('description', classname="full"),
    FieldPanel('organisation', classname="full organisation"),
    FieldPanel('amount_needed', classname="full amount needed"),
    FieldPanel('show_comments')
]
