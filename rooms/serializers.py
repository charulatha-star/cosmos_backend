from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    active_participants = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'type',
            'capacity',
            'description',
            'created_by',
            'created_by_name',
            'active_participants',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_active_participants(self, obj):
        # Can be dynamically populated from LiveKit or cache
        return []

    def validate(self, attrs):
        request = self.context.get('request')
        room_type = attrs.get('type', 'temporary')

        # PRD Section 3 rule: Only Admins can create permanent rooms
        if room_type == 'permanent' and request and request.user.role != 'Admin':
            raise serializers.ValidationError({"type": "Only Admins can create permanent rooms."})

        return attrs
