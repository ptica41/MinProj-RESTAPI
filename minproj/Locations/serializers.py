from Minapp.models import Location

from rest_framework import serializers


class LocationSerializer(serializers.ModelSerializer):
    department_name = serializers.StringRelatedField(source='department_id.name')
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Location
        fields = '__all__'

    def create(self, validated_data):
        return Location.objects.create(**validated_data)


class AdminPatchLocationSerializer(serializers.ModelSerializer):
    department_name = serializers.StringRelatedField(source='department_id.name')

    class Meta:
        model = Location
        fields = '__all__'

    def create(self, validated_data):
        return Location.objects.create(**validated_data)


class LocationOperatorSerializer(serializers.ModelSerializer):
    department_name = serializers.StringRelatedField(source='department_id.name')
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Location
        fields = '__all__'

    def validate(self, data):
        department_id = self.context['request'].user.department_id
        if data['department_id'] != department_id:
            data['department_id'] = department_id
        return data

    def create(self, validated_data):
        return Location.objects.create(**validated_data)
