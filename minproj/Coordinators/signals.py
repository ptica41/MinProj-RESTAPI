from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from Minapp.models import Coordinator, User
from django.conf import settings


@receiver(post_init, sender=Coordinator)
def notify_check_coordinator(sender, instance, **kwargs):
    instance.old_is_check = instance.is_check


@receiver(post_save, sender=Coordinator)
def notify_new_coordinator(sender, instance, created, **kwargs):
    senders = []
    if created:
        admins = User.objects.filter(is_superuser=True)
        for i in admins:
            senders.append(i.email)
        html_content = render_to_string('notify_new_coordinator.html', {'coordinator': instance, 'to_user': instance.user_id})
        msg = EmailMultiAlternatives(
            subject='Новая заявка: координатор',
            body='',
            from_email=settings.SERVER_EMAIL,
            to=senders
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        senders.clear()

    if instance.is_check == 1 and instance.old_is_check != instance.is_check:
        to_user = instance.user_id
        try:
            html_content = render_to_string('notify_check_coordinator.html', {'to_user': to_user})
            msg = EmailMultiAlternatives(
                subject='Ваша заявка одобрена',
                body='',
                from_email=settings.SERVER_EMAIL,
                to=[to_user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except:
            admins = User.objects.filter(is_superuser=True)
            for i in admins:
                senders.append(i.email)
            html_content = render_to_string('notify_check_coordinator.html',
                                            {'coordinator': instance, 'to_user': to_user})
            msg = EmailMultiAlternatives(
                subject='Письмо с подтверждением не доставлено',
                body='',
                from_email=settings.SERVER_EMAIL,
                to=senders
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()



