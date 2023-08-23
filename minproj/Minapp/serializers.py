import datetime

from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import serializers

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
        # предоставленные почта и пароль соответствуют какому-то пользователю в
        # нашей базе данных.
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'Пользователь с таким логином и паролем не найден'
            )

        user.last_login = datetime.datetime.now(tz=timezone.utc)
        user.save()

        # Метод validate должен возвращать словарь проверенных данных. Это
        # данные, которые передются в т.ч. в методы create и update.
        return {
            'username': user.username,
            'token': user.token,
            'staff': user.staff
        }
