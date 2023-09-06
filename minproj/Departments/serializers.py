from Minapp.models import Department

from rest_framework import serializers


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

    def create(self, validated_data):
        return Department.objects.create(**validated_data)