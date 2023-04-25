import uuid
import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phone_field import PhoneField

from common.abstract_models import DateBaseModel, AbstractSiteModel
from common.managers import CustomUserManager


# Create your models here.

class User(AbstractUser, DateBaseModel, AbstractSiteModel):

    ADMIN = 'admin'
    MANAGER = 'manager'
    MEMBER = 'member'

    USER_TYPES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (MEMBER, 'Member'),
    )

    username = models.CharField(
        max_length=100, verbose_name="Username", unique=True, blank=True,
        default=uuid.uuid4)
    first_name = models.CharField('First Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    email = models.EmailField('Email Address', unique=True)
    mobile = PhoneField(help_text='Mobile Number', blank=True, null=True)
    date_of_birth = models.DateField('Date of Birth', blank=True, null=True)
    user_type = models.CharField(
        'User Type', max_length=15, choices=USER_TYPES, default=MANAGER
    )
    family = models.ForeignKey(
        'Family', on_delete=models.CASCADE, verbose_name='Family',
        related_name='get_user', null=True
    )
    profile_picture = models.ImageField('Profile Picture', blank=True, null=True,
                                        upload_to='profile_pictures')
    location = models.CharField('Location', max_length=100, blank=True, null=True)
    is_verified = models.BooleanField('Verified', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User Details"
        verbose_name_plural = "User Details"
        ordering = ('-created',)
        unique_together = ['username', 'site']

    def __str__(self):
        return self.email

    @property
    def user_age(self):
        today = datetime.date.today()
        age = today.year - self.date_of_birth.year
        return age


class Family(DateBaseModel, AbstractSiteModel):
    """
    Model for storing Family
    """
    name = models.CharField(_('Name'), max_length=250)
    logo = models.ImageField(_("Logo"), upload_to='family logos/',
                             null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name='Created By',
        related_name='get_families', null=True
    )

    class Meta:
        verbose_name = "Family"
        verbose_name_plural = "Families"
        ordering = ('-created',)

    def __str__(self):
        return self.name

    
class FamilyContactDetails(DateBaseModel, AbstractSiteModel):
    """
    Contact details
    """
    family = models.OneToOneField(
        Family, on_delete=models.CASCADE, verbose_name='Family',
        related_name='get_contact_detail'
    )
    phone_number = models.CharField('Phone Number', max_length=15)
    alternate_phone_number = models.CharField('Alternate Phone Number',max_length=15, blank=True, null=True)
    email = models.EmailField('Email')
    alternate_email = models.EmailField('Alternate Email', blank=True, null=True)

    class Meta:
        verbose_name = "Family Contact Detail"
        verbose_name_plural = "Family Contact Details"
        ordering = ('-created',)

    def __str__(self):
        return self.family.name


class SubDomain(DateBaseModel, AbstractSiteModel):
    """
    Family subdomain
    """
    name = models.CharField(_("Domain Name"), max_length=100, unique=True)
    family = models.OneToOneField(
        Family, on_delete=models.CASCADE, verbose_name=_("Family"),
        related_name='get_sub_domain', null=True
    )

    class Meta:
        verbose_name = "SubDomain"
        verbose_name_plural = "SubDomains"
        ordering = ('-created',)

    def __str__(self):
        return '%s %s' % (self.name, self.family.name)
