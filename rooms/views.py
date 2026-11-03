import datetime
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from livekit import api
from .models import Room
from .serializers import RoomSerializer

def get_livekit_client():
    return api.RoomServiceClient(
        settings.LIVEKIT_URL,
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    )

class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.all().order_by('-created_at')
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomDetailDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        is_admin = request.user.role == 'Admin'
        is_creator = room.created_by == request.user

        # Admin can delete any room; Employee can only delete their own temporary room
        if is_admin or (room.type == 'temporary' and is_creator):
            room.delete()
            return Response({"message": "Room deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"detail": "You do not have permission to delete this room."},
            status=status.HTTP_403_FORBIDDEN
        )

class RoomTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)

        # Generate short-lived LiveKit AccessToken
        token = (
            api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(str(request.user.id))
            .with_name(request.user.name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=str(room.id),
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            # Short-lived token expires in 1 hour (PRD Section 6.3 requirement)
            .with_ttl(datetime.timedelta(hours=1))
        )

        jwt_token = token.to_jwt()

        return Response({
            "token": jwt_token,
            "server_url": settings.LIVEKIT_URL,
            "room_name": room.name,
            "participant_identity": str(request.user.id),
        }, status=status.HTTP_200_OK)

class RoomModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def check_moderator_permission(self, request, room):
        # PRD Section 3: Only Admin or the room Host can moderate
        return request.user.role == 'Admin' or room.created_by == request.user

    def post(self, request, room_id, participant_identity, action=None):
        room = get_object_or_404(Room, id=room_id)
        if not self.check_moderator_permission(request, room):
            return Response(
                {"detail": "Only Admins or Hosts can moderate participants."},
                status=status.HTTP_403_FORBIDDEN
            )

        client = get_livekit_client()

        try:
            if action == "mute":
                track_sid = request.data.get("track_sid")
                client.mute_published_track(
                    api.MuteRoomTrackRequest(
                        room=str(room.id),
                        identity=participant_identity,
                        track_sid=track_sid,
                        muted=True
                    )
                )
                return Response({"message": "Participant muted successfully."})

            elif action == "remove":
                client.remove_participant(
                    api.RoomParticipantIdentity(
                        room=str(room.id),
                        identity=participant_identity
                    )
                )
                return Response({"message": "Participant removed from room."})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Invalid moderation action."}, status=status.HTTP_400_BAD_REQUEST)

class EndRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if request.user.role != 'Admin' and room.created_by != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            client = get_livekit_client()
            client.delete_room(api.DeleteRoomRequest(room=str(room.id)))
        except Exception:
            pass

        return Response({"message": "Room closed for all participants."})
