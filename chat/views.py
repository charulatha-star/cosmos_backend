from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from rooms.models import Room
from accounts.models import User
from accounts.serializers import UserSerializer

class RoomMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        messages = Message.objects.filter(room=room, is_direct=False).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"detail": "Message text cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            room=room,
            text=text,
            is_direct=False
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DirectMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        messages = Message.objects.filter(
            is_direct=True
        ).filter(
            (Q(sender=request.user) & Q(recipient=other_user)) |
            (Q(sender=other_user) & Q(recipient=request.user))
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        recipient = get_object_or_404(User, id=user_id)
        text = request.data.get('text', '').strip()
        if not text:
            return Response({"detail": "Message text cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            text=text,
            is_direct=True
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatContactsView(APIView):
    """
    Returns available team members in the office to start direct messages with.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        teammates = User.objects.exclude(id=request.user.id).order_by('name')
        return Response(UserSerializer(teammates, many=True).data, status=status.HTTP_200_OK)
