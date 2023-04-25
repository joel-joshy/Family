from datetime import date

from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from apps.survey.models import Survey
from apps.survey.serializers import SurveyListCreateSerializer, \
    SurveyDescriptionSerializer
from apps.usermanagement.permissions import IsAnyManager


class SurveyListCreateAPIView(generics.ListCreateAPIView):
    """
    Survey List and Create
    """
    serializer_class = SurveyListCreateSerializer
    permission_classes = [IsAuthenticated, IsAnyManager]

    def get_queryset(self):
        status = self.request.GET.get('status', '')
        family = self.request.user.family
        queryset = family.get_surveys.all()
        if status == 'active':
            queryset = queryset.filter(
                Q(expiry_date__gte=date.today()) |
                Q(expiry_date=None)
            )
        elif status == 'expired':
            queryset = queryset.filter(expiry_date__lt=date.today())
        return queryset


class SurveyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Survey detail api view
    """
    permission_classes = [IsAuthenticated, IsAnyManager]
    serializer_class = SurveyListCreateSerializer

    def get_queryset(self):
        family = self.request.user.family
        queryset = family.get_surveys.all()
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.is_published = False
        instance.save()
        # instance.get_results.all().delete()
        data = {
            'status': True,
            'message': "Survey moved to deleted surveys"
        }
        return Response(data=data, status=HTTP_200_OK)


class AnonymousUserSurveyDetailAPIView(generics.RetrieveAPIView):

    queryset = Survey.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SurveyDescriptionSerializer
    lookup_field = 'survey_uuid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        current_date = date.today()
        if instance.expiry_date:
            if current_date > instance.expiry_date:
                data = {
                    "status": False, "error": None,
                    "message": 'Survey has expired', 'data': {}
                }
                return Response(data=data, status=HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)