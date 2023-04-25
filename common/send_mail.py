import logging

from django.conf import settings

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


logger = logging.getLogger(__name__)


def send_mail(contact, subject, html_content):
    """
    sending email to user
    """
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=contact,
        subject=subject,
        html_content=html_content)
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        logger.info('Cannot send email %s ' % e)