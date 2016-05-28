from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsearch import index


class FundRaiser(Page):
    description = RichTextField(blank=True)
    paypal_account = models.CharField(max_length=250)
    iban_number = models.CharField(max_length=250)

    search_fields = Page.search_fields + (
        index.SearchField('name'),
        index.SearchField('description'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('description', classname="full"),
        FieldPanel('paypal_account'),
        FieldPanel('iban_number')

    ]

class Project(Page):
    fund_raiser = models.ForeignKey(FundRaiser, related_name='projects', on_delete=models.CASCADE)
    amount = models.IntegerField()
    description = RichTextField(blank=True)
    organisation = models.CharField(max_length=250)

    search_fields = Page.search_fields + (
        index.SearchField('description'),
        index.SearchField('organisation'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('fund_raiser'),
        FieldPanel('description', classname="full"),
        FieldPanel('amount'),
        FieldPanel('organisation')
    ]