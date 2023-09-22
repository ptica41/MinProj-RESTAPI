from rest_framework import serializers

from Minapp.models import Location


class LocationSerializer(serializers.ModelSerializer):
    department_id_id = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Location
        exclude = ['lat', 'lon']
        depth = 1

    def validate(self, data):
        user = self.context['request'].user
        if self.context['request'].method == 'POST':
            if user.staff == 'AD' and not ('department_id_id' in data):
                raise serializers.ValidationError('department_id_id is required')
        if user.staff == 'OP':
            data['department_id_id'] = user.department_id.id
        return data

    def create(self, validated_data):
        return Location.objects.create(**validated_data)


