import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import User, UserGroups


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    staff = serializers.CharField(max_length=2, read_only=True)

    def validate(self, data):
        # В методе validate мы убеждаемся, что текущий экземпляр
        # LoginSerializer значение valid. В случае входа пользователя в систему
        # это означает подтверждение того, что присутствуют адрес электронной
        # почты и то, что эта комбинация соответствует одному из пользователей.
        phone = data.get('phone', None)
        password = data.get('password', None)

        if phone is None:
            raise serializers.ValidationError('Введите номер телефона')

        if password is None:
            raise serializers.ValidationError('Введите пароль')

        # Метод authenticate предоставляется Django и выполняет проверку, что
        # предоставленные логин и пароль соответствуют какому-то пользователю в
        # нашей базе данных.
        user = authenticate(phone=phone, password=password)

        if user is None:
            print('adawd')
            raise serializers.ValidationError('Пользователь с таким логином и паролем не найден')

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
            'phone': user.phone,
            'token': Token.objects.get(user=user).key,
            'staff': user.staff
        }


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    staff = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department_id_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        exclude = ['user_permissions']
        depth = 1


    def validate(self, data):

        if self.context['request'].method == 'POST':
            if self.context['request'].user.staff == 'AD':
                if not ('staff' in data):
                    raise serializers.ValidationError("Поле 'staff' обязательно")
                if not ('email' in data) and (data['staff'] == 'OP' or data['staff'] == 'CO'):
                    raise serializers.ValidationError("При создании пользователя с ролью 'OP' или 'CO' поле 'email' обязательно")
                if not ('department_id_id' in data) and data['staff'] == 'OP':
                    raise serializers.ValidationError("При создании пользователя с ролью 'OP' поле 'department_id_id' обязательно")
                if 'department_id_id' in data and data['staff'] != 'OP':
                    raise serializers.ValidationError("Поле 'department_id_id' только при создании пользователя с ролью 'OP' ")
            elif self.context['request'].user.staff == 'OP':
                data['staff'] = 'RE'
                data['is_check'] = False
                data['is_superuser'] = False
                data['is_active'] = True
                data['department_id_id'] = None
            elif self.context['request'].user.staff == 'CO':
                data['staff'] = 'RE'
                data['is_check'] = True
                data['is_superuser'] = False
                data['is_active'] = True
                data['department_id_id'] = None

        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    is_check = serializers.BooleanField(read_only=True)
    staff = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    department_id_id = serializers.IntegerField(read_only=True)

    # def validate(self, data):
    #     department_id = self.context['request'].user.department_id
    #     if data.get['department_id_id'] != department_id:
    #         data['department_id_id'] = department_id
    #     return data

    class Meta:
        model = User
        exclude = ['is_superuser', 'user_permissions']
        depth = 1

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class PatchRecipientCoordinatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['is_check', 'is_active']


class UserGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGroups
        exclude = ['user']
        depth = 1

    def create(self, validated_data):
        return UserGroups.objects.create(**validated_data)
