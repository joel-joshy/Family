from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.module_loading import import_string

from drfpasswordless.settings import api_settings
from drfpasswordless.utils import create_callback_token_for_user, logger

from rest_framework.authtoken.models import Token

from common.send_mail import send_mail
from common.send_sms import send_sms


def user_login_data(request, user, token_key=None):
    family = user.family
    subdomain = user.site
    if not token_key:
        token, _ = Token.objects.get_or_create(user=user)
        token_key = token.key
    data = {
        'token': token_key, 'user_id': user.id,
        'first_name': user.first_name, 'last_name': user.last_name,
        'email': user.email, 'username': user.username,
        'mobile': user.mobile.raw_phone if user.mobile else None,
        'family_id': family.id,
        'family': family.name, 'user_type': user.user_type, 'is_profile_completed': user.is_verified,
        'logo': request.build_absolute_uri(family.logo.url) if family.logo else None,
        'profile_picture': request.build_absolute_uri(
            user.profile_picture.url) if user.profile_picture else None,
        'subdomain': subdomain.domain,
    }
    return data


def send_email_with_callback_token(request, user, email_token, **kwargs):
    """
    Sends a Email to user.email.

    Passes silently without sending in test environment
    """
    try:
        # import pdb;
        # pdb.set_trace()
        user_email = [getattr(
            user, api_settings.PASSWORDLESS_USER_EMAIL_FIELD_NAME)]
        # if os.getenv('PROJECT_ENV') == 'PRODUCTION':
        #     static_url = 'https://%s' % settings.AWS_S3_CUSTOM_DOMAIN
        # else:
        static_url = get_current_site(request)
        subject = 'Family : Your Login OTP'
        template_name = 'registration/passwordless_token.html'
        message = render_to_string(
            template_name=template_name,
            context={
                'callback_token': email_token.key,
                'username': user.get_full_name(),
                'static_url': static_url
            }
        )
        print("OTP: {otp}".format(otp=email_token.key))
        # message.content_subtype = "html"
        send_mail(user_email, subject, message)
        return True
    except Exception as e:
        logger.debug("Failed to send token email to user: %d."
                     "Possibly no email on user object. Email entered was %s" %
                     (user.id, getattr(
                         user, api_settings.PASSWORDLESS_USER_EMAIL_FIELD_NAME
                     )))
        logger.debug(e)
        return False


def send_sms_with_callback_token(request, user, mobile_token, **kwargs):
    """
    Sends a SMS to user.mobile via Twilio.
    Passes silently without sending in test environment.
    """
    # import pdb; pdb.set_trace()
    # if api_settings.PASSWORDLESS_TEST_SUPPRESSION is True:
    #     # we assume success to prevent spamming SMS during testing.
    #
    #     # even if you have suppression on– you must provide a number if you have mobile selected.
    #     if api_settings.PASSWORDLESS_MOBILE_NOREPLY_NUMBER is None:
    #         return False
    #
    #     return True

    # base_string = kwargs.get('mobile_message',
    #                          api_settings.PASSWORDLESS_MOBILE_MESSAGE)
    no_reply_number = '+15675571448'

    try:
        if no_reply_number:
            # no_reply_number = api_settings.PASSWORDLESS_MOBILE_NOREPLY_NUMBER
            to_number = getattr(user,
                                api_settings.PASSWORDLESS_USER_MOBILE_FIELD_NAME)
            if to_number.__class__.__name__ == 'PhoneNumber':
                to_number = to_number.__str__()
            body = "Hi {name} ,\nUse this OTP to log in: {otp}".format(name=user.first_name if user.first_name else "Family User", otp=mobile_token.key)
            send_sms(body, to_number)
            return True
    #     else:
    #         logger.debug(
    #             "Failed to send token sms. Missing PASSWORDLESS_MOBILE_NOREPLY_NUMBER.")
    #         return False
    # except ImportError:
    #     logger.debug("Couldn't import Twilio client. Is twilio installed?")
    #     return False
    # except KeyError:
    #     logger.debug("Couldn't send SMS."
    #                  "Did you set your Twilio account tokens and specify a PASSWORDLESS_MOBILE_NOREPLY_NUMBER?")
    except Exception as e:
        logger.debug("Failed to send token SMS to user: {}. "
                     "Possibly no mobile number on user object or the twilio package isn't set up yet. "
                     "Number entered was {}".format(user.id, getattr(user,
                                                                     api_settings.PASSWORDLESS_USER_MOBILE_FIELD_NAME)))
        logger.debug(e)
        return False


class TokenService(object):
    @staticmethod
    def send_token(request, user, alias_type, token_type, **message_payload):
        # import pdb;
        # pdb.set_trace()

        token = create_callback_token_for_user(user, alias_type, token_type)
        send_action = None
        if user.pk in api_settings.PASSWORDLESS_DEMO_USERS.keys():
            return True
        if alias_type == 'email':
            send_action = send_email_with_callback_token(
                request, user, token, **message_payload)
        elif alias_type == 'mobile':
            # send_action = import_string(api_settings.PASSWORDLESS_SMS_CALLBACK)
            send_action = send_sms_with_callback_token(
                request, user, token, **message_payload)

        # Send to alias
        # success = send_action(user, token, **message_payload)
        return send_action