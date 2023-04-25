from django.urls import path

from apps.survey import views

urlpatterns = [
    path('survey-list-create/', views.SurveyListCreateAPIView.as_view(),
         name='survey-list-create'),
    path('survey-details/<int:pk>/', views.SurveyDetailAPIView.as_view(),
         name='survey-details'),
    path('attend/<uuid:survey_uuid>/',
         views.AnonymousUserSurveyDetailAPIView.as_view(),
         name='anonymous-survey'),
]