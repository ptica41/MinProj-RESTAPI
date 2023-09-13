from Minapp.models import Group

from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        return Group.objects.create(**validated_data)


class AdminGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

    def create(self, validated_data):
        return Group.objects.create(**validated_data)


