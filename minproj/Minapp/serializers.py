import datetime
import pytz

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    staff = serializers.CharField(max_length=2, read_only=True)

    def validate(self, data):
        # В методе validate мы убеждаемся, что текущий экземпляр
        # LoginSerializer значение valid. В случае входа пользователя в систему
        # это означает подтверждение того, что присутствуют адрес электронной
        # почты и то, что эта комбинация соответствует одному из пользователей.
        username = data.get('username', None)
        password = data.get('password', None)

        if username is None:
            raise serializers.ValidationError(
                'Введите логин'
            )

        if password is None:
            raise serializers.ValidationError(
                'Введите пароль'
            )

        # Метод authenticate предоставляется Django и выполняет проверку, что
        # предоставленные логин и пароль соответствуют какому-то пользователю в
        # нашей базе данных.
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'Пользователь с таким логином и паролем не найден'
            )

        user.last_login = datetime.datetime.now(tz=timezone.utc)
        user.save()
        try:
            token = Token.objects.get(user=user)

            if token.created.timestamp() < (datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=30)).timestamp():
                # update the created time of the token to keep it valid
                token.delete()
                token = Token.objects.create(user=user)
                token.created = datetime.datetime.now(tz=timezone.utc)
                token.save()
        except ObjectDoesNotExist:
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.now(tz=timezone.utc)
            token.save()

                # Метод validate должен возвращать словарь проверенных данных. Это
        # данные, которые передются в т.ч. в методы create и update.
        return {
            'username': user.username,
            'token': Token.objects.get(user=user).key,
            'staff': user.staff
        }
