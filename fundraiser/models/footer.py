from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet

@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class FooterSnippet(models.Model):
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255)
    text = models.TextField()

    panels = [
        FieldPanel('url'),
        FieldPanel('title'),
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.title