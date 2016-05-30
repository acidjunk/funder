from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


class projectIndexPage(Page):
    @property
    def projects(self):
        # Get list of blog pages that are descendants of this page
        projects = ProjectPage.objects.descendant_of(self).live()
        projects = projects.order_by(
            '-date'
        )
        return projects

    class Meta:
        verbose_name = _('Projects index')

    subpage_types = ['fundraiser.ProjectPage']


class ProjectPage(Page):
    amount = models.IntegerField()
    description = RichTextField(blank=True)
    organisation = models.CharField(max_length=250, blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + (
        index.SearchField('description'),
        index.SearchField('organisation'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
        FieldPanel('amount'),
        FieldPanel('organisation')
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        ImageChooserPanel('feed_image'),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['fundraiser.ProjectIndexPage']
    subpage_types = []