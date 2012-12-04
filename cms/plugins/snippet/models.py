from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin


class SnippetPtr(CMSPlugin):
    template = models.CharField(_("template"), max_length=100, choices=getattr(settings, 'CMS_SNIPPET_TEMPLATES', []))

    class Meta:
        verbose_name = _("Snippet")

    def __unicode__(self):
        return self.get_template_display()

