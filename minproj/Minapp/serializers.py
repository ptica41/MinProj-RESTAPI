import datetime
import pytz

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User, UserGroups, Department  # Operator, Coordinator, Recipient


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

            if token.created.timestamp() < (
                    datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=30)).timestamp():
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


class CreateUserSerializer(serializers.ModelSerializer):  # только для Администраторов
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    email = serializers.EmailField(allow_null=True)
    middle_name = serializers.CharField(allow_null=True)
    staff = serializers.CharField(required=True)

    class Meta:
        model = User
        exclude = ['is_superuser', 'user_permissions']


    def validate(self, data):
        if not ('email' in data) and (data['staff'] == 'OP' or data['staff'] == 'CO'):
            raise serializers.ValidationError("При создании пользователя с ролью 'OP' или 'CO' поле 'email' обязательно")
        if not ('department_id' in data) and data['staff'] == 'OP':
            raise serializers.ValidationError("При создании пользователя с ролью 'OP' поле 'department_id' обязательно")
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    # department_name = serializers.StringRelatedField(source='department_id.name')
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    is_check = serializers.BooleanField(read_only=True)
    staff = serializers.CharField(read_only=True)

    def validate(self, data):
        department_id = self.context['request'].user.department_id
        if data['department_id'] != department_id:
            data['department_id'] = department_id
        return data

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['is_superuser', 'user_permissions']
        depth = 1


class PatchUserAdminSerializer(serializers.ModelSerializer):
    # department_name = serializers.StringRelatedField(source='department_id.name')
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['user_permissions']


class PatchRecipientCoordinatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['is_check']


class UserGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGroups
        exclude = ['user']
        depth = 1

    def create(self, validated_data):
        return UserGroups.objects.create(**validated_data)
