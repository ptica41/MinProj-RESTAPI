from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, get_password_validators

from rest_framework import serializers, status, exceptions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.authtoken.models import Token

from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm
from django_rest_passwordreset.models import clear_expired, get_password_reset_lookup_field, ResetPasswordToken
from django_rest_passwordreset.views import HTTP_USER_AGENT_HEADER, HTTP_IP_ADDRESS_HEADER

from Minapp.views import user_response, BearerToken, IsAuth
from Minapp.models import User
from .serializers import PhoneSerializer, ResetPasswordSerializer


class MyResetPasswordRequestToken(ResetPasswordRequestToken):

    serializer_class = PhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        # before we continue, delete all existing expired tokens
        password_reset_token_validation_time = 24*7

        # datetime.now minus expiry hours
        now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)

        # delete all tokens where created_at < now - 24 hours
        clear_expired(now_minus_expiry_time)

        # find a user by email address (case insensitive search)
        users = User.objects.filter(**{'{}__iexact'.format(get_password_reset_lookup_field()): phone})

        active_user_found = False

        # iterate over all users and check if there is any user that is active
        # also check whether the password can be changed (is useable), as there could be users that are not allowed
        # to change their password (e.g., LDAP user)
        for user in users:
            if user.eligible_for_reset():
                active_user_found = True
                break

        # No active user found, raise a validation error
        # but not if DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE == True
        if not active_user_found and not getattr(settings, 'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE', False):
            return Response(user_response(False, "Incorrect data", 400, "We couldn't find an account associated with that phone or the user isn't active",
                                          exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)

        # last but not least: iterate over all users that are active and can change their password
        # and create a Reset Password Token and send a signal with the created token
        for user in users:
            if user.eligible_for_reset():
                # define the token as none for now
                token = None

                # check if the user already has a token
                if user.password_reset_tokens.all().count() > 0:
                    # yes, already has a token, re-use this token
                    token = user.password_reset_tokens.all()[0]
                else:
                    # no token exists, generate a new token
                    token = ResetPasswordToken.objects.create(
                        user=user,
                        user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ''),
                        ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ''),
                    )
                # send a signal that the password token was created
                # let whoever receives this signal handle sending the email for the password reset
                # reset_password_token_created.send(sender=self.__class__, instance=self, reset_password_token=token)
        # done
        return Response(user_response(True, "Key generated successful", 200, {'staff': token.user.staff, 'user_id': token.user.id}), status=status.HTTP_200_OK)


class ListReset(ListAPIView):

    serializer_class = ResetPasswordSerializer
    authentication_classes = (BearerToken,)
    permission_classes = (IsAuth,)
    ordering_fields = '__all__'
    filterset_fields = {
        "created_at": ["lte", "gte"]
    }

    def get_queryset(self):  # получение нужного набора запросов в зависимости от роли пользователя
        token = self.request.META.get('HTTP_AUTHORIZATION')
        user_id = Token.objects.get(key=token.split(' ')[1]).user_id
        user = User.objects.get(id=user_id)

        if user.staff == 'AD':
            return ResetPasswordToken.objects.exclude(user__staff='RE')
        elif user.staff == 'CO' and user.is_active and user.is_check:
            return ResetPasswordToken.objects.filter(user__staff='RE')
        else:
            raise serializers.ValidationError(user_response(False, "Permission denied", 403, None, "ValidationError"))

    def list(self, request, *args, **kwargs):  # изменение response body
        response = super().list(request, *args, **kwargs)
        return Response(user_response(True, "List was send successful", 200, response.data), status=status.HTTP_200_OK)


class MyResetPasswordConfirm(ResetPasswordConfirm):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        password = request.data.get('password', {})
        token = request.data.get('token', {})
        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()

        if not reset_password_token:
            return Response(user_response(False, "Incorrect data", 400, "The key wasn't found", exception="ValidationError"), status=status.HTTP_400_BAD_REQUEST)

        # change users password (if we got to this code it means that the user is_active)
        if reset_password_token.user.eligible_for_reset():
            try:
                # validate the password against existing validators
                validate_password(
                    password,
                    user=reset_password_token.user,
                    password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
                )
            except ValidationError as e:
                # raise a validation error for the serializer
                raise exceptions.ValidationError({
                    'password': e.messages
                })

            reset_password_token.user.set_password(password)
            reset_password_token.user.save()

        # Delete all password reset tokens for this user
        ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

        return Response(user_response(True, "Password was patched successful", 200, {'status': 'OK'}), status=status.HTTP_200_OK)
