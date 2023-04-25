from django.db import models
from django.utils.translation import gettext_lazy as _

from common.managers import CurrentSiteManager


class DateBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-modified',)

    @property
    def created_date(self):
        return self.created.date()


class AbstractSiteModel(models.Model):
    site = models.ForeignKey(
        'sites.Site', on_delete=models.CASCADE, verbose_name=_("Site"),
        default=2
    )
    objects = CurrentSiteManager()

    class Meta:
        abstract = True
