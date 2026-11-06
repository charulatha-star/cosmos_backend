from rest_framework import serializers
from .models import Presence

class PresenceSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    user_name = serializers.ReadOnlyField(source='user.name')
    user_email = serializers.ReadOnlyField(source='user.email')
    user_role = serializers.ReadOnlyField(source='user.role')

    class Meta:
        model = Presence
        fields = [
            'user_id',
            'user_name',
            'user_email',
            'user_role',
            'status',
            'current_space',
            'current_desk',
            'x',
            'y',
            'updated_at',
        ]
