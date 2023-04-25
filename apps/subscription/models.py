from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext as _
from django.db.models import JSONField

from apps.usermanagement.models import User, Family
from common.abstract_models import DateBaseModel


class Plan(DateBaseModel):
    """
    Model for subscription plans.
    """
    PER_YEAR = "per_year"
    PER_MONTH = "per_month"

    TERM_CHOICES = (
        (PER_MONTH, 'per month'),
        (PER_YEAR, 'per year')
    )
    name = models.CharField(_("Plan Name"), max_length=200)
    price = models.DecimalField(_("Plan Price"), max_digits=12,
                                decimal_places=2, default=1.00,
                                validators=[MinValueValidator(1.00)])
    max_members = models.IntegerField(_("Maximum Members"), default=1,
                                      validators=[MinValueValidator(1)])
    term = models.CharField(_("Plan Term"), max_length=10,
                            choices=TERM_CHOICES, default=PER_MONTH)
    is_active = models.BooleanField(_("Is Active"),
                                    help_text=_("Is active or not"),
                                    default=True)
    stripe_id = models.CharField(_("Stripe ID"), max_length=200,
                                 null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        ordering = ('-created',)


class Transaction(DateBaseModel):
    """
    Model for transactions details.
    """
    transaction_id = models.CharField(
        _("Transaction ID"), max_length=150, null=True, blank=True
    )
    amount = models.DecimalField(_("Amount"), max_digits=12,
                                 decimal_places=2, null=True)
    coupon = models.CharField(_("Coupon"), max_length=150, null=True,
                              blank=True)
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, verbose_name=_("Plan"),
        related_name="get_transactions", null=True
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name=_("User Transaction"),
        related_name="get_transactions", null=True
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, verbose_name=_("Family"),
        related_name="get_transactions", null=True
    )
    completed_date = models.DateTimeField(_("Completed Date"), null=True,
                                          blank=True)
    invoice_url = models.URLField(_("Invoice URL"), null=True, blank=True)
    customer_id = models.CharField(_("Stripe Customer ID"), max_length=150,
                                   null=True, blank=True)
    details = JSONField(_("Transaction Details"), blank=True, null=True)

    def __str__(self):
        return '%s - %s - %s' % (self.plan, self.user, self.transaction_id)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ('-created',)



class Subscription(DateBaseModel):
    """
    Model for storing subscriptions
    """
    ACTIVE = 'active'
    CANCELED = 'canceled'
    INCOMPLETE = 'incomplete'
    UNPAID = 'unpaid'
    PAST_DUE = 'past_due'
    INCOMPLETE_EXPIRED = 'incomplete_expired'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (CANCELED, 'Canceled'),
        (INCOMPLETE, 'Incomplete'),
        (UNPAID, 'Unpaid'),
        (PAST_DUE, 'Past Due'),
        (INCOMPLETE_EXPIRED, 'Incomplete Expired')
    )

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name=_("User Subscription"),
        related_name="get_subscriptions", null=True
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, verbose_name=_("Plan"),
        related_name="get_subscriptions", null=True
    )
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, verbose_name=_("Family"),
        related_name="get_subscriptions"
    )
    stripe_id = models.CharField(_("Stripe Subscription"), max_length=150,
                                 unique=True)
    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"))
    details = JSONField(_("Subscription Details"), blank=True, null=True)
    status = models.CharField(_("Subscription Status"), max_length=50,
                              choices=STATUS_CHOICES, default=ACTIVE)
    is_trial_plan = models.BooleanField(_("Is Trial Plan"), default=Family)

    def __str__(self):
        return '%s - %s - %s' % (self.plan, self.user, self.stripe_id)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ('-created',)




