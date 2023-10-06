from rest_framework import serializers

from django_rest_passwordreset.models import ResetPasswordToken
from Minapp.models import User


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()


class ResetPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = ResetPasswordToken
        fields = ['id', 'key', 'user', 'created_at', 'ip_address', 'user_agent']
        depth = 1
