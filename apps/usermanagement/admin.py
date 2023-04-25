from django.contrib import admin

from apps.usermanagement.models import Family, User, FamilyContactDetails, \
    SubDomain


# Register your models here.


class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active')
    fields = ['name', 'created_by', 'logo', 'is_active', 'site']
    search_fields = ['name']
    list_filter = ['created_by', 'is_active']


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'family',
                    'mobile', 'is_verified')
    fields = [
        'username', 'email', 'first_name', 'last_name', 'user_type', 'family', 'mobile',
        'date_of_birth', 'profile_picture', 'location', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'site',
    ]

    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'user_type', 'family__name'
    ]

    list_filter = [
        'user_type', 'family', 'mobile', 'is_verified', 'is_active', 'is_superuser'
    ]


class FamilyContactDetailsAdmin(admin.ModelAdmin):
    list_display = [
        'family', 'email', 'alternate_email', 'phone_number',
        'alternate_phone_number'
    ]
    fields = [
        'family', 'email', 'alternate_email', 'phone_number',
        'alternate_phone_number'
    ]
    search_fields = [
        'family__name', 'email', 'alternate_email', 'phone_number',
        'alternate_phone_number'
    ]


class SubDomainAdmin(admin.ModelAdmin):
    list_display = ['name', 'family', 'site']
    fields = ['name', 'family', 'site']
    search_fields = ["name", "family__name", "site__name"]


admin.site.register(Family, FamilyAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(SubDomain, SubDomainAdmin)
admin.site.register(FamilyContactDetails, FamilyContactDetailsAdmin)
