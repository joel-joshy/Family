import os

from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import RegexValidator
from drfpasswordless.models import CallbackToken
from drfpasswordless.serializers import TokenField
from drfpasswordless.settings import api_settings
from drfpasswordless.utils import validate_token_age, verify_user_alias
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.usermanagement.models import User, Family, FamilyContactDetails, \
    SubDomain
from common.send_sms import send_sms


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer
    """
    family = serializers.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'family']

    def validate(self, data):
        request = self.context.get('request')
        current_site = Site.objects.filter(domain=request.site).first()
        user = User.objects.filter(email=data['email']).first()
        if user and user.site == current_site:
            raise serializers.ValidationError(
                {
                    'status': False,
                    'error': 'User with this email already exists',
                }
            )
        if not data.get('family'):
            raise serializers.ValidationError(
                {
                    'status': False,
                    'error': 'Please enter your family'
                    ,
                }
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            site=request.site
        )
        user.set_unusable_password()

        family = Family.objects.create(
            created_by=user, name=validated_data['family'],
            site=request.site
        )
        # print(family)
        user.family = family
        user.save()

        data = {
            'user': user.username,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'family': family.name,
            'is_profile_completed': user.is_verified
        }
        return {'status': True, 'error': None, 'data': data}


def token_age_validator(value):
    valid_token = validate_token_age(value)
    if not valid_token:
        raise serializers.ValidationError("Wrong OTP, please try again")
    return value


class AbstractBaseCallbackTokenSerializer(serializers.Serializer):
    """
    Abstract class inspired by DRF's own token serializer.
    Returns a user if valid, None or a message if not.
    """
    phone_regex = RegexValidator(regex=r'^\+[1-9]\d{1,14}$',
                                 message="Mobile number must be entered in the format:"
                                         " '+999999999'. Up to 15 digits allowed.")

    email = serializers.EmailField(required=False)  # Needs to be required=false to require both.
    mobile = serializers.CharField(required=False, validators=[phone_regex], max_length=17)
    token = TokenField(min_length=6, max_length=6, validators=[token_age_validator])

    def validate_alias(self, attrs):
        email = attrs.get('email', None)
        mobile = attrs.get('mobile', None)

        if email and mobile:
            raise serializers.ValidationError()

        if not email and not mobile:
            raise serializers.ValidationError()

        if email:
            return 'email', email
        elif mobile:
            return 'mobile', mobile

        return None


class CallbackTokenAuthSerializer(AbstractBaseCallbackTokenSerializer):

    def validate(self, attrs):
        # Check Aliases
        try:
            alias_type, alias = self.validate_alias(attrs)
            callback_token = attrs.get('token', None)
            user = User.objects.get(**{alias_type+'__iexact': alias})
            token = CallbackToken.objects.get(**{'user': user,
                                                 'key': callback_token,
                                                 'type': CallbackToken.TOKEN_TYPE_AUTH,
                                                 'is_active': True})

            if token.user == user:
                # Check the token type for our uni-auth method.
                # authenticates and checks the expiry of the callback token.
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)

                if api_settings.PASSWORDLESS_USER_MARK_EMAIL_VERIFIED \
                        or api_settings.PASSWORDLESS_USER_MARK_MOBILE_VERIFIED:
                    # Mark this alias as verified
                    user = User.objects.get(pk=token.user.pk)
                    success = verify_user_alias(user, token)

                    if success is False:
                        msg = 'Error validating user alias.'
                        raise serializers.ValidationError(msg)

                attrs['user'] = user
                return attrs

            else:
                msg = 'Invalid Token'
                raise serializers.ValidationError(msg)
        except CallbackToken.DoesNotExist:
            msg = 'Invalid alias parameters provided.'
            raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            msg = 'Invalid user alias parameters provided.'
            raise serializers.ValidationError(msg)
        except ValidationError:
            msg = 'Invalid alias parameters provided.'
            raise serializers.ValidationError(msg)


class FamilyContactusSerializer(serializers.ModelSerializer):

    family_id = serializers.ReadOnlyField(source='family.id')
    family_name = serializers.ReadOnlyField(source='family.name')

    class Meta:
        model = FamilyContactDetails
        fields = ('id', 'family_id', 'family_name', 'phone_number', 'email',
                  'alternate_phone_number', 'alternate_email')


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer to complete registration.
    """

    class Meta:
        model = User
        fields = ['date_of_birth', 'location', 'mobile']

    def validate(self, data):
        location = data['location']
        date_of_birth = data['date_of_birth']
        mobile = data['mobile']
        if not location:
            raise serializers.ValidationError(
                {'status': False,
                 'error': {'errorMessage': "Enter Location"},
                 'data': {}}
            )
        if not date_of_birth:
            raise serializers.ValidationError(
                {'status': False,
                 'error': {'errorMessage': "Enter Date of Birth"},
                 'data': {}}
            )
        if not mobile:
            raise serializers.ValidationError(
                {'status': False,
                 'error': {'errorMessage': "Enter mobile number"},
                 'data': {}}
            )
        return data


class CreateSubDomainSerializer(serializers.ModelSerializer):
    """
    Serializer for creating subdomain
    """
    class Meta:
        model = SubDomain
        fields = ['name']

    def validate(self, data):
        name = data['name'].lower()
        request = self.context.get('request')
        user = request.user
        family = user.family
        site = Site.objects.filter(domain=name).first()
        if site:
            raise serializers.ValidationError(
                {'status': False,
                 'error': {'errorMessage': "Domain name already exists"},
                 'data': {}}
            )
        subdomain = SubDomain.objects.filter(family=family).first()
        if subdomain:
            raise serializers.ValidationError(
                {'status': False,
                 'error': {
                     'errorMessage':
                         "Domain already exists for the family"
                 },
                 'data': {}}
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        family = user.family
        name = validated_data['name'].lower()
        site = Site.objects.create(domain=name, name=name)
        subdomain = SubDomain.objects.create(
            name=name, family=family, site=site
        )
        family.site = site
        family.save()
        if user.mobile:
            body = 'Hi {name} ,\nYour subdomain for {family} has been ' \
                   'successfully created. ' \
                   'Login to your subdomain by clicking this link. \n' \
                   '{subdomain}'.format(
                    name=user.first_name if user.first_name else "Family User",
                    family=user.family.name,
                    subdomain=subdomain.name)

            send_sms(body, to_number=user.mobile.raw_phone)
        user.site = site
        user.save()
        data = {'user_id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'is_profile_completed': user.is_verified,
                'institution': family.name,
                'subdomain': subdomain.name,
                'message': 'Sub Domain created successfully'}
        return {'status': True, 'error': None, 'data': data}


class ProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile details
    """
    family_name = serializers.ReadOnlyField(source='family.name')
    age = serializers.ReadOnlyField(source='user_age')

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'mobile',
            'user_type', 'family', 'family_name', 'date_of_birth',
            'profile_picture', 'location', 'is_verified', 'date_joined', 'age'
        ]


class AddIndividualMemberSerializer(serializers.ModelSerializer):
    """
    Serializer to add individual member
    """
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'mobile', 'email'
        ]

    def validate(self, data):
        request = self.context.get('request')
        first_name = data.get('first_name')
        email = data.get('email')
        if not email:
            raise serializers.ValidationError(
                {
                    'status': False,
                    'error': {
                        'errorMessage': 'Email is required'
                    }
                }
            )
        else:
            if not first_name:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        'error': {
                            'errorMessage': 'First name is required'
                        }
                    }
                )
            user = User.objects.filter(email=email).first()
            if user:
                raise serializers.ValidationError(
                    {
                        'status': False,
                        'error': {
                            'errorMessage': 'Email is already in use'
                        }
                    }
                )
        return data