from django.contrib import admin
from apps.survey.models import Survey


class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'created_by', 'family', 'survey_uuid',
        'expiry_date', 'is_private', 'is_active', 'is_published'
    ]
    fields = [
        'name', 'created_by', 'family',
        'description', 'survey_uuid', 'demographic_questions',
        'general_questions', 'expiry_date', 'link', 'qr_code', 'is_private',
        'is_active', 'is_published',
        'site'
    ]
    search_fields = [
        'name', 'created_by__email', 'family__name',
        'demographic_questions', 'general_questions', 'description'
    ]
    list_filter = [
        'created_by', 'family', 'is_private', 'is_active', 'is_published'
    ]


admin.site.register(Survey, SurveyAdmin)