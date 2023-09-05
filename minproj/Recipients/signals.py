# from django.db.models.signals import post_save, post_init
# from django.dispatch import receiver
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from Minapp.models import Recipient, User
# from django.conf import settings
#
#
# @receiver(post_init, sender=Recipient)
# def notify_check_recipient(sender, instance, **kwargs):
#     instance.old_is_check = instance.is_check
#
#
# @receiver(post_save, sender=Recipient)
# def notify_new_recipient(sender, instance, created, **kwargs):
#     senders = []
#     if created:
#         staff = User.objects.filter(staff='CO')
#         for i in staff:
#             senders.append(i.email)
#         html_content = render_to_string('notify_new_recipient.html', {'recipient': instance, 'to_user': instance.user_id})
#         msg = EmailMultiAlternatives(
#             subject='Новая заявка: получатель',
#             body='',
#             from_email=settings.SERVER_EMAIL,
#             to=senders
#         )
#         msg.attach_alternative(html_content, "text/html")
#         msg.send()
#         senders.clear()
#
#     if instance.is_check == 1 and instance.old_is_check != instance.is_check:
#         to_user = instance.user_id
#         try:
#             staff = User.objects.filter(staff='OP')
#             for i in staff:
#                 senders.append(i.email)
#             html_content = render_to_string('check_new_recipient.html', {'to_user': to_user})
#             msg = EmailMultiAlternatives(
#                 subject='Новый получатель',
#                 body='',
#                 from_email=settings.SERVER_EMAIL,
#                 to=senders
#             )
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()
#             senders.clear()
#
#             if to_user.email:
#                 html_content = render_to_string('notify_check_recipient.html', {'to_user': to_user})
#                 msg = EmailMultiAlternatives(
#                     subject='Заявка одобрена',
#                     body='',
#                     from_email=settings.SERVER_EMAIL,
#                     to=[to_user.email]
#                 )
#                 msg.attach_alternative(html_content, "text/html")
#                 msg.send()
#
#         except:
#             staff = User.objects.filter(staff='CO')
#             for i in staff:
#                 senders.append(i.email)
#             html_content = render_to_string('notify_check_recipient.html',
#                                             {'to_user': to_user})
#             msg = EmailMultiAlternatives(
#                 subject='Письмо с подтверждением не доставлено',
#                 body='',
#                 from_email=settings.SERVER_EMAIL,
#                 to=senders
#             )
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()
#             senders.clear()
#
#
