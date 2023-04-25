from django.urls import path

from rest_framework.routers import DefaultRouter

from apps.usermanagement import views

app_name = 'useraccount'

router = DefaultRouter()
router.register(r'contact-us', views.FamilyContactusView, basename='contact-us')

urlpatterns = [
    path('register/', views.UserRegisterAPIView.as_view(), name='register'),
    path('auth/email/', views.ObtainEmailCallbackToken.as_view(), name='obtain_email_callback_token'),
    path('auth/token/', views.ObtainAuthTokenFromCallbackToken.as_view(), name='obtain_auth_token_from_callback_token'),
    path('auth/mobile/', views.ObtainMobileCallbackToken.as_view(), name='obtain_mobile_callback_token'),
    path('complete-registration/<int:pk>/',
         views.CompleteRegistrationView.as_view(), name='complete_registration'),

    path('create-subdomain/', views.CreateSubdomainAPIView.as_view(),
         name='create_subdomain'),
    path('profile/<int:pk>/', views.ProfileDetailAPIView.as_view(), name='profile_detail'),
    path('add-member-individual/', views.AddIndividualMemberAPIView.as_view(),
         name='add_individual_member'),
]
urlpatterns += router.urls