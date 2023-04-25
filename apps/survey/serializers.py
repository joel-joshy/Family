from datetime import datetime

from rest_framework import serializers

from apps.survey.models import Survey


class SurveyListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to list and create survey
    """
    created_date = serializers.ReadOnlyField()
    family = serializers.ReadOnlyField(source='family.name')
    creator_name = serializers.ReadOnlyField(source='created_by.get_full_name')

    class Meta:
        model = Survey
        fields = [
            'id', 'name', 'creator_name', 'created_date', 'family',
            'description', 'demographic_questions', 'general_questions',
            'expiry_date', 'link', 'survey_uuid', 'is_survey_expired',
            'is_active', 'is_published', 'is_private' ,'qr_code'
        ]

    def validate(self, attrs):
        name = attrs.get('name')
        expiry_date = attrs.get('expiry_date')
        if not name:
            raise serializers.ValidationError(
                {
                    'status': False,
                    'error': {
                        'error_message': 'Enter a name for the survey'
                    },
                    'data': {}
                }
            )
        if expiry_date:
            if expiry_date < datetime.now().date():
                raise serializers.ValidationError(
                    {
                        'status': False,
                        'error': {
                            'error_message': 'Please enter a valid date'
                        },
                        'data': {}
                    }
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        survey = Survey.objects.create(
            created_by=user, family=user.family, site=request.site,
            **validated_data
        )
        return survey


class SurveyDescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer to show the details of a survey
    """
    created_date = serializers.ReadOnlyField()
    family = serializers.ReadOnlyField(source='family.name')
    creator_name = serializers.ReadOnlyField(source='created_by.get_full_name')
    family_logo = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = [
            'id', 'name', 'creator_name', 'description', 'created_date',
            'family', 'expiry_date', 'demographic_questions',
            'general_questions', 'family_logo'
        ]

    def get_family_logo(self, obj):
        request = self.context.get('request')
        logo_url = request.build_absolute_uri(
            obj.family.logo.url
        ) if obj.family.logo else None
        return logo_url