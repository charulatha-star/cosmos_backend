from django.urls import path
from .views import (
    RoomListCreateView,
    RoomDetailDeleteView,
    RoomTokenView,
    RoomModerationView,
    EndRoomView,
)

urlpatterns = [
    path('', RoomListCreateView.as_view(), name='room-list-create'),
    path('<uuid:room_id>/', RoomDetailDeleteView.as_view(), name='room-detail-delete'),
    path('<uuid:room_id>/token/', RoomTokenView.as_view(), name='room-token'),
    path('<uuid:room_id>/participants/<str:participant_identity>/<str:action>/', RoomModerationView.as_view(), name='room-moderate'),
    path('<uuid:room_id>/end/', EndRoomView.as_view(), name='room-end'),
]
