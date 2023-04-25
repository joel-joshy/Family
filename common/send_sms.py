from twilio.rest import Client

from django.conf import settings


twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
no_reply_number = settings.NO_REPLY_NUMBER


def send_sms(body, to_number):
    otp = twilio_client.messages.create(
        body=body,
        to=to_number,
        from_=no_reply_number
    )
    print(otp.body)