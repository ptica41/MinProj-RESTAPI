from Minapp.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """ Сериализация регистрации пользователя и создания нового. """

    # Убедитесь, что пароль содержит не менее 8 символов, не более 128,
    # и так же что он не может быть прочитан клиентской стороной
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    # Клиентская сторона не должна иметь возможность отправлять токен вместе с
    # запросом на регистрацию. Сделаем его доступным только на чтение.
    token = serializers.CharField(max_length=255, read_only=True)
    email = serializers.EmailField(required=True)
    staff = serializers.CharField(default='CO')

    class Meta:
        model = User
        fields = ['phone', 'name', 'surname', 'middle_name', 'staff', 'email', 'photo', 'password', 'token']
        depth = 1

    def validate(self, data):
        data['staff'] = 'CO'
        data['is_check'] = False
        return data

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return User.objects.create_user(**validated_data)
