from Minapp.models import Group

from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        return Group.objects.create(**validated_data)

