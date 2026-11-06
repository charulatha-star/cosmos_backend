import datetime
import uuid
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from livekit import api
from .models import Room, Space
from .serializers import RoomSerializer

# This function creates a connection between our Django backend and LiveKit.
# Think of LiveKit as the service that manages video and audio meetings.
# So, Whenever we want to perform actions like muting or removing participants, we use this client.
def get_livekit_client():
    return api.RoomServiceClient(
        settings.LIVEKIT_URL, # where livekit is running
        settings.LIVEKIT_API_KEY, # identifies our application
        settings.LIVEKIT_API_SECRET # authenticates our backend.
    )

class SpaceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        spaces = Space.objects.all()
        if not spaces.exists():
            # Seed default space 'billion' if empty (matching real Cosmos screenshot)
            default_space = Space.objects.create(
                id='billion',
                name='billion',
                owner=request.user,
                admin_access=True,
                is_free=True
            )
            spaces = [default_space]

        data = [{
            'id': s.id,
            'name': s.name,
            'admin_access': s.admin_access,
            'is_free': s.is_free,
            'created_at': s.created_at,
        } for s in spaces]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({"detail": "Space name is required."}, status=status.HTTP_400_BAD_REQUEST)

        slug = name.lower().replace(' ', '-') + '-' + str(uuid.uuid4())[:6]
        space = Space.objects.create(
            id=slug,
            name=name,
            owner=request.user,
            admin_access=True,
            is_free=True
        )
        return Response({
            'id': space.id,
            'name': space.name,
            'admin_access': space.admin_access,
            'is_free': space.is_free,
        }, status=status.HTTP_201_CREATED)

# To create and view rooms
class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # GET: display the all rooms available in the system.
    def get(self, request):
        rooms = Room.objects.all().order_by('-created_at')
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST: create a new room. Only Admins can create permanent rooms, while Employees can only create temporary rooms.
    def post(self, request):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# To view and delete a specific room, generate LiveKit tokens, moderate participants, and end rooms based on their roles and permissions.
class RoomDetailDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    # GET: view details of a specific room.
    def get(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE: remove a room. Only Admins can delete any room, while Employees can only delete their own temporary rooms.
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

# This view generates a LiveKit token for a user to join a specific room. The token is short-lived (1 hour) and contains the necessary permissions for the user to join, publish, and subscribe in the room.
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

        # Converts the access token into a JWT string.
        jwt_token = token.to_jwt()

        return Response({
            "token": jwt_token,
            "server_url": settings.LIVEKIT_URL,
            "room_name": room.name,
            "participant_identity": str(request.user.id),
        }, status=status.HTTP_200_OK)

# To mute or remove participants
class RoomModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def check_moderator_permission(self, request, room):
        # Only Admin or the room Host can moderate
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

# To end a meeting for everyone. Only Admins or the room Host can end a meeting.
class EndRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, id=room_id)
        if request.user.role != 'Admin' and room.created_by != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            client = get_livekit_client() # this sends a request to LiveKit to end the room for all participants. It doesn't delete the room from our database, but it effectively ends the meeting session.
            client.delete_room(api.DeleteRoomRequest(room=str(room.id)))
        except Exception:
            pass

        return Response({"message": "Room closed for all participants."})





# It allows users to list, create, retrieve, delete rooms, generate LiveKit tokens, moderate participants, and end rooms based on their roles and permissions.
# Create video meeting rooms.


# View all available rooms.


# View individual room details.


# Delete rooms based on their role.


# Join a room using a LiveKit token.


# Mute or remove participants.


# End a meeting for everyone.