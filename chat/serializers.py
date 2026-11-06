from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.ReadOnlyField(source='sender.id')
    sender_name = serializers.ReadOnlyField(source='sender.name')
    sender_role = serializers.ReadOnlyField(source='sender.role')
    recipient_name = serializers.ReadOnlyField(source='recipient.name')

    class Meta:
        model = Message
        fields = [
            'id',
            'sender_id',
            'sender_name',
            'sender_role',
            'room',
            'recipient',
            'recipient_name',
            'text',
            'is_direct',
            'created_at',
        ]
        read_only_fields = ['id', 'sender_id', 'sender_name', 'sender_role', 'created_at']
