import datetime
import uuid
import qrcode

from io import BytesIO
from PIL import Image, ImageDraw

from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext as _
from django.core.files import File
from django.contrib.postgres.fields import ArrayField

from apps.usermanagement.models import User, Family

from common.abstract_models import DateBaseModel, AbstractSiteModel


# Create your models here.

class Survey(DateBaseModel, AbstractSiteModel):
    """
    Model for surveys
    """
    name = models.CharField(_("Name"), max_length=250)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="get_surveys",
        verbose_name=_("Created By"), null=True
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="get_surveys",
        verbose_name=_("Family"), null=True
    )
    description = models.TextField(_("Description"), null=True, blank=True)
    demographic_questions = JSONField(
        _("Demographic Questions"), help_text=_("Demographic Questions and "
                                                "choices in JSON format"),
                                                null=True, blank=True
        )
    general_questions = JSONField(
        _("General Questions"), help_text=_("General Questions and choices "
                                            "in JSON format"), null=True,
                                            blank=True
        )
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    is_private = models.BooleanField(_("Is Private"), default=False)
    is_active = models.BooleanField(_("Is Active"), default=True)
    is_published = models.BooleanField(_("Is Published"), default=False)
    link = models.URLField(_("Link"), null=True, blank=True)
    survey_uuid = models.CharField(_("Survey UUID"), max_length=100,
                                   unique=True, default=uuid.uuid4)
    qr_code = models.ImageField(_("QR Code"), upload_to='qr_codes', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        sub_domain = self.family.get_sub_domain.name
        if not self.id:
            survey_link = sub_domain + '/api/survey/attend/' + str(
                self.survey_uuid) + "/"
            self.link = survey_link
        if self.link and not self.qr_code:
            qrcode_img = qrcode.make(self.link)
            canvas = Image.new('RGB', (500, 500), 'white')
            draw = ImageDraw.Draw(canvas)
            canvas.paste(qrcode_img)
            file_name = f'qr_code-{self.name}.png'
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            self.qr_code.save(file_name, File(buffer), save=False)
            canvas.close()
        super(Survey, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "survey"
        verbose_name_plural = "Surveys"
        ordering = ('-created',)

    @property
    def is_survey_expired(self):
        if self.expiry_date:
            return True if datetime.date.today() > self.expiry_date else False
        return False


# class SurveyDefaultDemographicQuestions(DateBaseModel, AbstractSiteModel):
#     """
#     Default Demographic Questions
#     """
#     question = models.TextField(_("Question"))
#     choices = ArrayField(models.CharField(
#         max_length=250, blank=True, help_text=_("Separate choices by comma")
#     ))
#
#     class Meta:
#         verbose_name = 'Survey Default Demographic Question'
#         verbose_name_plural = 'Survey Default Demographic Questions'
#         ordering = ('-created',)
#
#     def __str__(self):
#         return self.question