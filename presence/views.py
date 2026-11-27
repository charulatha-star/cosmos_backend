from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Presence
from .serializers import PresenceSerializer

class PresenceListView(APIView):
    """
    List presence status and live positions for all team members in the office.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        space = request.query_params.get('space', 'billion')
        # Ensure requesting user has an active presence record starting at Reception Area
        Presence.objects.get_or_create(
            user=request.user,
            defaults={
                'current_space': space,
                'current_desk': 'Reception Area',
                'x': 270,
                'y': 725,
            }
        )
        presences = Presence.objects.select_related('user').filter(current_space=space)
        serializer = PresenceSerializer(presences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PresenceUpdateView(APIView):
    """
    Update the current user's live avatar coordinates and presence status.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        presence, _ = Presence.objects.get_or_create(user=request.user)

        user_status = request.data.get('status')
        if user_status in ['online', 'busy', 'in_room', 'offline']:
            presence.status = user_status
            request.user.status = user_status
            request.user.save(update_fields=['status'])

        if 'x' in request.data:
            presence.x = int(request.data['x'])
        if 'y' in request.data:
            presence.y = int(request.data['y'])
        if 'desk' in request.data:
            presence.current_desk = request.data['desk']
        if 'space' in request.data:
            presence.current_space = request.data['space']
        if 'is_camera_on' in request.data:
            presence.is_camera_on = bool(request.data['is_camera_on'])
        if 'is_muted' in request.data:
            presence.is_muted = bool(request.data['is_muted'])

        presence.save()
        serializer = PresenceSerializer(presence)
        return Response(serializer.data, status=status.HTTP_200_OK)
