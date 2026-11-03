import datetime
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from livekit import api
from .models import Room


class RoomTokenView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)


        # 1. Generate short-lived LiveKit AccessToken
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
            # Token expires in 1 hour (PRD Section 6.3 requirement)
            .with_ttl(datetime.timedelta(hours=1))
        )


        jwt_token = token.to_jwt()


        return Response({
            "token": jwt_token,
            "server_url": settings.LIVEKIT_URL,
            "room_name": room.name,
            "participant_identity": str(request.user.id),
        }, status=status.HTTP_200_OK)



# ============
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from livekit import api
from .models import Room


def get_livekit_client():
    return api.RoomServiceClient(
        settings.LIVEKIT_URL,
        settings.LIVEKIT_API_KEY,
        settings.LIVEKIT_API_SECRET
    )


class RoomModerationView(APIView):
    permission_classes = [IsAuthenticated]


    def check_moderator_permission(self, request, room):
        # PRD Section 3: Only Admin or the room Host can moderate
        is_admin = request.user.role == 'Admin'
        is_host = room.created_by == request.user
        return is_admin or is_host


    # Endpoint: Remote Mute Participant Track
    # POST /api/rooms/<room_id>/participants/<participant_identity>/mute/
    def post(self, request, room_id, participant_identity, action=None):
        room = get_object_or_404(Room, id=room_id)
        if not self.check_moderator_permission(request, room):
            return Response({"detail": "Only Admins or Hosts can moderate participants."}, status=status.HTTP_403_FORBIDDEN)


        client = get_livekit_client()


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
            # Endpoint: Disconnect / Kick participant from room
            client.remove_participant(
                api.RoomParticipantIdentity(
                    room=str(room.id),
                    identity=participant_identity
                )
            )
            return Response({"message": "Participant removed from room."})


class EndRoomView(APIView):
    permission_classes = [IsAuthenticated]


    # POST /api/rooms/<room_id>/end/
    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if request.user.role != 'Admin' and room.created_by != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


        client = get_livekit_client()
        # Closes the WebRTC room and disconnects everyone (PRD Section 7)
        client.delete_room(api.DeleteRoomRequest(room=str(room.id)))
        return Response({"message": "Room closed for all participants."})