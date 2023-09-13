from Minapp.models import Event, Location, User, Group

from rest_framework import serializers


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'
        depth = 1

    def validate(self, data):
        if 'recipient_id' in data and 'group_id' in data:
            raise serializers.ValidationError("Only recipient_id or group_id must be")
        if not ('recipient_id' in data or 'group_id' in data):
            raise serializers.ValidationError("Recipient_id or group_id is required")
        if not ('datetime' in data or 'start' in data or 'end' in data):
            raise serializers.ValidationError("Datetime or start or end is required")
        user = self.context['request'].user
        if user.staff == 'OP' and user.department_id != data['location_id'].department_id:
            raise serializers.ValidationError("Location's Department must be equal Operator's Department")
        if user.staff == 'OP' and not data['location_id'].is_active:
            raise serializers.ValidationError("Location isn't active")
        if 'recipient_id' in data:
            if data['recipient_id'].staff != 'RE':
                raise serializers.ValidationError("Id in request isn't a recipient's id")
            if user.staff == 'OP' and not (data['recipient_id'].is_active and data['recipient_id'].is_check):
                raise serializers.ValidationError("Recipient isn't active or check")
        if 'group_id' in data:
            if user.staff == 'OP' and not data['group_id'].is_active:
                raise serializers.ValidationError("Group isn't active or exist")
        return data

    def create(self, validated_data):
        return Event.objects.create(**validated_data)


class PatchEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'
        depth = 1

    def validate(self, data):
        if 'recipient_id' in data and 'group_id' in data:
            raise serializers.ValidationError("Only recipient_id or group_id must be")
        if not ('recipient_id' in data or 'group_id' in data):
            raise serializers.ValidationError("Recipient_id or group_id is required")
        if not ('datetime' in data or 'start' in data or 'end' in data):
            raise serializers.ValidationError("Datetime or start or end is required")
        user = self.context['request'].user
        if user.staff == 'OP' and user.department_id != data['location_id'].department_id:
            raise serializers.ValidationError("Location's Department must be equal Operator's Department")
        if user.staff == 'OP' and not data['location_id'].is_active:
            raise serializers.ValidationError("Location isn't active")
        if 'recipient_id' in data:
            if data['recipient_id'].staff != 'RE':
                raise serializers.ValidationError("Id in request isn't a recipient's id")
            if user.staff == 'OP' and not (data['recipient_id'].is_active and data['recipient_id'].is_check):
                raise serializers.ValidationError("Recipient isn't active or check")
        if 'group_id' in data:
            if user.staff == 'OP' and not data['group_id'].is_active:
                raise serializers.ValidationError("Group isn't active or exist")
        return data

    def create(self, validated_data):
        return Event.objects.create(**validated_data)


class CoordinatorEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['is_check']