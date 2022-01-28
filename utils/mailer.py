from celery import shared_task
from django.core.mail import send_mail

from core_config import settings


def send_email(subject, message, recipient_list):
    email_from = settings.EMAIL_HOST_USER
    send_mail(
        subject, message, email_from, recipient_list
    )
    return True


def send_email_with_template(template, recipient_list, context):
    email_from = settings.EMAIL_HOST_USER
    try:
        email = EmailTemplate.objects.get(name=template)
        send_mail(
            email.subject.format(**context),
            email.content.format(**context),
            email_from,
            recipient_list
        )
    except EmailTemplate.DoesNotExist:
        return False
    except KeyError:
        return False
    return True


@shared_task(bind=True)
def task_send_email(*args, **kwargs):
    receivers = kwargs['receivers']
    template = kwargs.get('template')
    if not isinstance(receivers, (list, tuple)):
        receivers = [receivers]
    if template:
        send_email_with_template(template, receivers, kwargs.get('context'))
    else:
        send_email(kwargs.get('subject'), receivers, kwargs.get('message'))
    return True
