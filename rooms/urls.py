from django.urls import path
from .views import RoomTokenView
from .views import RoomModerationView, EndRoomView


urlpatterns = [
    path('rooms/<uuid:room_id>/token/', RoomTokenView.as_view(), name='room-token'),
    path('rooms/<uuid:room_id>/participants/<str:participant_identity>/<str:action>/', RoomModerationView.as_view(), name='room-moderate'),
    path('rooms/<uuid:room_id>/end/', EndRoomView.as_view(), name='room-end'),
]

