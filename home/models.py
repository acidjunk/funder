from __future__ import unicode_literals

from modelcluster.fields import ParentalKey
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField

from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel, MultiFieldPanel)

from fundraiser.models import ProductPage, ProjectPage

class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)
        context['recent_products'] = ProductPage.objects.all().order_by('-id')[0:5]
        context['recent_projects'] = ProjectPage.objects.all().order_by('-id')[0:5]
        return context

class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')

class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldPanel('to_address', classname="full"),
            FieldPanel('from_address', classname="full"),
            FieldPanel('subject', classname="full"),
        ], "Email")
    ]