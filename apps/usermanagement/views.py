from django.contrib.sites.models import Site
from dj_rest_auth.views import PasswordResetView
from django.utils.module_loading import import_string
from drfpasswordless.models import CallbackToken
from drfpasswordless.serializers import EmailAuthSerializer, logger, \
    MobileAuthSerializer
from drfpasswordless.settings import api_settings

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets


from apps.usermanagement import serializers
from apps.usermanagement.models import User, FamilyContactDetails, Family
from apps.usermanagement.serializers import CallbackTokenAuthSerializer, \
    FamilyContactusSerializer, CreateSubDomainSerializer, \
    ProfileDetailSerializer
from apps.usermanagement.utils import user_login_data, TokenService
from common.utils import get_queryset_for_current_site, send_invitation_message
from apps.usermanagement.permissions import IsAnyManager

# Create your views here.


class UserRegisterAPIView(generics.CreateAPIView, PasswordResetView):
    """User Register API View"""
    serializer_class = serializers.UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)


class AbstractBaseObtainCallbackTokenEmail(APIView):

    success_response = "A login token has been sent to you"
    failure_response = "Unable to send you a login code, try again later"

    message_payload = {}

    @property
    def serializer_class(self):
        raise NotImplementedError

    @property
    def alias_type(self):
        raise NotImplementedError

    @property
    def token_type(self):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        if self.alias_type.upper() not in api_settings.PASSWORDLESS_AUTH_TYPES:
            return Response(status=status.HTTP_404_NOT_FOUND)
        email = request.data.get('email')
        origin = request.META.get('HTTP_ORIGIN')
        user = User.objects.filter(email=email, site__domain=origin).first()
        if user:
            success = TokenService.send_token(request, user,
                                              self.alias_type,
                                              self.token_type,
                                              **self.message_payload)
            if success:
                status_code = status.HTTP_200_OK
                response_detail = self.success_response
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                response_detail = self.failure_response
            return Response({'detail': response_detail}, status=status_code)
        else:
            return Response(
                data={'status': False,
                      'error': {
                          'error_message': "Email ID does not exist"
                      }
                      },
                status=status.HTTP_400_BAD_REQUEST
            )


class ObtainEmailCallbackToken(AbstractBaseObtainCallbackTokenEmail):
    permission_classes = (AllowAny,)
    serializer_class = EmailAuthSerializer
    success_response = "A login token has been sent to you"
    failure_response = "Unable to send you a login code, try again later"

    alias_type = 'email'
    token_type = CallbackToken.TOKEN_TYPE_AUTH

    email_subject = api_settings.PASSWORDLESS_EMAIL_SUBJECT
    email_plaintext = api_settings.PASSWORDLESS_EMAIL_PLAINTEXT_MESSAGE
    email_html = api_settings.PASSWORDLESS_EMAIL_TOKEN_HTML_TEMPLATE_NAME
    message_payload = {
        'email_subject': email_subject,
        'email_plaintext': email_plaintext,
        'email_html': email_html
    }


class AbstractBaseObtainAuthToken(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            if user.site.domain == request.META.get('HTTP_ORIGIN'):
                token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
                (token, _) = token_creator(user)
                if token:
                    TokenSerializer = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_SERIALIZER)
                    token_serializer = TokenSerializer(data=token.__dict__, partial=True)
                    if token_serializer.is_valid():
                        data = user_login_data(
                            request, user, token_key=token.key
                        )
                        return Response(
                            {'status': True, 'error': None, 'data': data}
                        )
            else:
                return Response(
                    data={'status': False,
                          'error': {
                              'error_message': "User does not exist"
                          }},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            logger.error("Couldn't log in unknown user."
                         "Errors on serializer: {}".format(serializer.error_messages))
            return Response(
                {'detail': 'Couldn\'t log in unknown user.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AbstractBaseObtainCallbackTokenMobile(APIView):

    success_response = "A login token has been sent to you"
    failure_response = "Unable to send you a login code, try again later"

    message_payload = {}

    @property
    def serializer_class(self):
        raise NotImplementedError

    @property
    def alias_type(self):
        raise NotImplementedError

    @property
    def token_type(self):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        if self.alias_type.upper() not in api_settings.PASSWORDLESS_AUTH_TYPES:
            return Response(status=status.HTTP_404_NOT_FOUND)
        mobile = request.data.get('mobile')
        origin = request.META.get('HTTP_ORIGIN')
        user = User.objects.filter(mobile=mobile, site__domain=origin).first()
        if user:
            success = TokenService.send_token(request, user,
                                              self.alias_type,
                                              self.token_type,
                                              **self.message_payload)
            if success:
                status_code = status.HTTP_200_OK
                response_detail = self.success_response
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                response_detail = self.failure_response
            return Response({'detail': response_detail}, status=status_code)
        else:
            return Response(
                data={'status': False,
                      'error': {
                          'error_message': "Mobile number does not exist"
                      }
                      },
                status=status.HTTP_400_BAD_REQUEST
            )


class ObtainAuthTokenFromCallbackToken(AbstractBaseObtainAuthToken):
    permission_classes = (AllowAny,)
    serializer_class = CallbackTokenAuthSerializer


class ObtainMobileCallbackToken(AbstractBaseObtainCallbackTokenMobile):
    permission_classes = (AllowAny,)
    serializer_class = MobileAuthSerializer

    success_response = "A login token has been sent to your mobile number"
    failure_response = "Unable to send you a login code, try again later"

    alias_type = 'mobile'
    token_type = CallbackToken.TOKEN_TYPE_AUTH

    mobile_message = api_settings.PASSWORDLESS_MOBILE_MESSAGE
    message_payload = {'mobile_message': mobile_message}


class FamilyContactusView(viewsets.ModelViewSet):
    """
    Family Contactus view
    """
    serializer_class = FamilyContactusSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):

        user = self.request.user
        family = user.family
        queryset = FamilyContactDetails.objects.filter(family=family)
        return queryset

    def create(self, request, *args, **kwargs):
        user = self.request.user
        family = user.family
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(family=family, site=request.site)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class CompleteRegistrationView(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.CompleteRegistrationSerializer

    def get_queryset(self):
        objects = get_queryset_for_current_site(
            User, self.request).all()
        return objects

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        user = self.request.user
        family = user.family
        if not family:
            family = Family.objects.create(
                created_by=user, name=request.data.get('family'),
                site=request.site
            )
            user.family = family
        user.is_verified = True
        user.save()
        data = {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'date_of_birth': user.date_of_birth,
            'mobile': user.mobile,
            'location': user.location,
            'family': family.name,
            'is_verified': user.is_verified,
        }
        return Response(data={'status': True, 'error': None, 'data': data},
                        status=status.HTTP_200_OK)


class CreateSubdomainAPIView(generics.CreateAPIView):
    serializer_class = CreateSubDomainSerializer
    permission_classes = [IsAuthenticated, IsAnyManager]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data=data, status=status.HTTP_200_OK)


class ProfileDetailAPIView(generics.RetrieveAPIView):
    """
    Profile Detail View
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileDetailSerializer

    def get_queryset(self):
        profile = get_queryset_for_current_site(
            User, self.request).filter(
            id=self.request.user.id
        )
        return profile


class AddIndividualMemberAPIView(generics.CreateAPIView):
    """
    API view for adding individual member
    """
    serializer_class = serializers.AddIndividualMemberSerializer
    permission_classes = [IsAuthenticated, IsAnyManager]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        family = self.request.user.family
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        email = request.data.get('email')
        subdomain = family.get_sub_domain
        site = Site.objects.filter(domain=subdomain.name).first()
        users = []
        if email and first_name:
            user = serializer.save(user_type=User.MEMBER, family=family,
                                   site=site)
            user.is_verified = True
            user.set_unusable_password()
            user.save()
            if user:
                if user.mobile:
                    send_invitation_message(user)
                users.append({'id': user.id, 'email': user.email,
                             'subdomain': user.site.domain})
        return Response(data={'status': True, 'error': None, 'data': {
            'users': users}, 'message': 'User has been added'},
                        status=status.HTTP_200_OK)