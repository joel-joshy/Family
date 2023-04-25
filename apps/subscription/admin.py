from django.contrib import admin
from apps.subscription.models import Plan, Transaction


# Register your models here.


class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'price', 'max_members', 'term', 'is_active', 'stripe_id'
    ]
    search_fields = ['name', 'price', 'max_members']
    list_filter = ['term', 'is_active']


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user_email', 'plan_name', 'coupon',
        'family_name', 'amount', 'completed_date'
    ]
    search_fields = [
        'transaction_id', 'user__email', 'plan__name',
        'family__name'
    ]
    list_filter = ['plan__name', 'user__email', 'family__name']

    def user_email(self, obj):
        return obj.user.email if obj.user else None

    def plan_name(self, obj):
        return obj.plan.name if obj.plan else None

    def family_name(self,obj):
        return obj.family.name if obj.family else None

admin.site.register(Plan, PlanAdmin)
admin.site.register(Transaction, TransactionAdmin)