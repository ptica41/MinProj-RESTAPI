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
    staff = serializers.CharField(default='OP')
    department_id_id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'surname', 'middle_name', 'staff', 'phone', 'email', 'photo', 'password', 'token',
                  'department_id_id']

    def validate(self, data):
        if data['staff'] != 'OP':
            data['staff'] = 'OP'
        return data

    def create(self, validated_data):
        # Использовать метод create_user, который мы
        # написали ранее, для создания нового пользователя.
        return User.objects.create_user(**validated_data)
