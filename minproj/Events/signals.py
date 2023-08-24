from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from Minapp.models import Event, User
from django.conf import settings


@receiver(post_init, sender=Event)
def notify_check_event(sender, instance, **kwargs):
    instance.old_is_check = instance.is_check


@receiver(post_save, sender=Event)
def notify_new_event(sender, instance, created, **kwargs):
    senders = []
    if created:
        staff = User.objects.filter(staff='CO')
        for i in staff:
            senders.append(i.email)
        html_content = render_to_string('notify_new_event.html', {'event': instance})
        msg = EmailMultiAlternatives(
            subject='Новая заявка: событие',
            body='',
            from_email=settings.SERVER_EMAIL,
            to=senders
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        senders.clear()

    if instance.is_check == 1 and instance.old_is_check != instance.is_check and instance.recipient_id.user_id.email:
        to_recipient = instance.recipient_id.user_id
        try:
            html_content = render_to_string('notify_check_event.html',
                                            {'recipient': to_recipient, 'event': instance})
            msg = EmailMultiAlternatives(
                subject='Новое событие',
                body='',
                from_email=settings.SERVER_EMAIL,
                to=[to_recipient.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except:
            staff = User.objects.filter(staff='CO')
            for i in staff:
                senders.append(i.email)
            html_content = render_to_string('notify_check_event.html',
                                            {'recipient': to_recipient, 'event': instance})
            msg = EmailMultiAlternatives(
                subject='Письмо с подтверждением не доставлено',
                body='',
                from_email=settings.SERVER_EMAIL,
                to=senders
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            senders.clear()


