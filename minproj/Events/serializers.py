from rest_framework import serializers

from Minapp.models import Event, Location, User, Group


class EventSerializer(serializers.ModelSerializer):
    is_check = serializers.BooleanField(read_only=True)
    location_id_id = serializers.IntegerField()
    recipient_id_id = serializers.IntegerField(allow_null=True)
    group_id_id = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Event
        fields = '__all__'
        depth = 1

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if ('recipient_id_id' in data) and ('group_id_id' in data):
                raise serializers.ValidationError("Only recipient_id_id or group_id_id must be")
            if not (('recipient_id_id' in data) or ('group_id_id' in data)):
                raise serializers.ValidationError("Recipient_id_id or group_id_id is required")
            if not (('datetime' in data) or ('start' in data) or ('end' in data)):
                raise serializers.ValidationError("Datetime or start or end is required")
            if not Location.objects.filter(id=data.get('location_id_id', None)).exists():
                raise serializers.ValidationError('Wrong location_id_id')
            user = self.context['request'].user
            if user.staff == 'OP' and user.department_id.id != Location.objects.get(id=data.get('location_id_id', None)).department_id.id:
                raise serializers.ValidationError("Location's Department must be equal Operator's Department")
            if user.staff == 'OP' and not Location.objects.get(id=data.get('location_id_id', None)).is_active:
                raise serializers.ValidationError("Location isn't active")
            if 'recipient_id_id' in data:
                if not User.objects.filter(id=data['recipient_id_id']).exists():
                    raise serializers.ValidationError("Id in request isn't a recipient's id")
                if User.objects.get(id=data['recipient_id_id']).staff != 'RE':
                    raise serializers.ValidationError("Id in request isn't a recipient's id")
                if user.staff == 'OP' and not (User.objects.get(id=data['recipient_id_id']).is_active and User.objects.get(id=data['recipient_id_id']).is_check):
                    raise serializers.ValidationError("Recipient isn't active or check")
            if 'group_id_id' in data:
                if not Group.objects.filter(id=data['group_id_id']).exists():
                    raise serializers.ValidationError('Wrong group_id_id')
                if user.staff == 'OP' and not Group.objects.get(id=data['group_id_id']).is_active:
                    raise serializers.ValidationError("Group isn't active or exist")
        return data

    def create(self, validated_data):
        return Event.objects.create(**validated_data)


class CoordinatorEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['is_check']


class AdminEventSerializer(serializers.ModelSerializer):
    location_id_id = serializers.IntegerField()
    recipient_id_id = serializers.IntegerField(allow_null=True, required=False)
    group_id_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = Event
        fields = '__all__'
        depth = 1

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if ('recipient_id_id' in data) and ('group_id_id' in data):
                raise serializers.ValidationError("Only recipient_id or group_id must be")
            if not (('recipient_id_id' in data) or ('group_id_id' in data)):
                raise serializers.ValidationError("Recipient_id_id or group_id_id is required")
            if not (('datetime' in data) or ('start' in data) or ('end' in data)):
                raise serializers.ValidationError("Datetime or start or end is required")
            if not Location.objects.filter(id=data.get('location_id_id', None)).exists():
                raise serializers.ValidationError('Wrong location_id_id')
            if 'recipient_id_id' in data:
                if not User.objects.filter(id=data['recipient_id_id']).exists():
                    raise serializers.ValidationError("Id in request isn't a recipient's id")
                if User.objects.get(id=data['recipient_id_id']).staff != 'RE':
                    raise serializers.ValidationError("Id in request isn't a recipient's id")
            if ('group_id_id' in data) and not Group.objects.filter(id=data['group_id_id']).exists():
                raise serializers.ValidationError('Wrong group_id_id')
        return data

    def create(self, validated_data):
        return Event.objects.create(**validated_data)
