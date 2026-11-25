from django.urls import path
from .views import (
    SpaceListView,
    SpaceSetupView,
    SpaceDetailDeleteView,
    SpaceMembersView,
    SpaceMemberDetailView,
    SpaceInvitationsView,
    SpaceInvitationActionView,
    EmailInvitationValidateView,
    EmailInvitationAcceptView,
    SpaceInviteView,
    InviteValidateView,
    InviteJoinView,
    GuestRoomValidateView,
    GuestRoomJoinView,
    GuestAccessRequestView,
    GuestAccessStatusView,
    AdminPendingGuestAccessView,
    AdminRespondGuestAccessView,
    RoomListCreateView,
    RoomDetailDeleteView,
    RoomTokenView,
    RoomModerationView,
    EndRoomView,
)
from chat.views import RoomMessagesView

urlpatterns = [
    # Spaces & Setup
    path('spaces/', SpaceListView.as_view(), name='space-list-create'),
    path('spaces/setup/', SpaceSetupView.as_view(), name='space-setup'),
    path('spaces/<str:space_id>/', SpaceDetailDeleteView.as_view(), name='space-detail-delete'),
    path('spaces/<str:space_id>/members/', SpaceMembersView.as_view(), name='space-members'),
    path('spaces/<str:space_id>/members/<uuid:member_id>/', SpaceMemberDetailView.as_view(), name='space-member-detail'),
    path('spaces/<str:space_id>/invitations/', SpaceInvitationsView.as_view(), name='space-invitations'),
    path('spaces/<str:space_id>/invitations/<uuid:invite_id>/<str:action>/', SpaceInvitationActionView.as_view(), name='space-invitation-action'),
    path('spaces/<str:space_id>/invite/', SpaceInviteView.as_view(), name='space-invite'),

    # Email invitation acceptance (token-based)
    path('invitations/<str:token>/', EmailInvitationValidateView.as_view(), name='email-invitation-validate'),
    path('invitations/<str:token>/accept/', EmailInvitationAcceptView.as_view(), name='email-invitation-accept'),


    # Public invite validation & join (Office Invitation)
    path('invite/<str:invite_code>/', InviteValidateView.as_view(), name='invite-validate'),
    path('invite/<str:invite_code>/join/', InviteJoinView.as_view(), name='invite-join'),

    # Public guest room invitation validation & join (Guest Room Invitation)
    path('invite/<str:invite_code>/guest-validate/', GuestRoomValidateView.as_view(), name='invite-guest-validate'),
    path('invite/<str:invite_code>/guest-join/', GuestRoomJoinView.as_view(), name='invite-guest-join'),

    # Guest Room Permission & Access Control
    path('spaces/<str:space_id>/guest-access/request/', GuestAccessRequestView.as_view(), name='guest-access-request'),
    path('spaces/<str:space_id>/guest-access/status/', GuestAccessStatusView.as_view(), name='guest-access-status'),
    path('spaces/<str:space_id>/guest-access/pending/', AdminPendingGuestAccessView.as_view(), name='admin-pending-guest-access'),
    path('spaces/<str:space_id>/guest-access/<uuid:request_id>/respond/', AdminRespondGuestAccessView.as_view(), name='admin-respond-guest-access'),

    # Rooms
    path('', RoomListCreateView.as_view(), name='room-list-create'),
    path('<uuid:room_id>/', RoomDetailDeleteView.as_view(), name='room-detail-delete'),
    path('<str:room_id>/token/', RoomTokenView.as_view(), name='room-token'),
    path('<str:room_id>/messages/', RoomMessagesView.as_view(), name='room-messages'),
    path('<str:room_id>/participants/<str:participant_identity>/<str:action>/', RoomModerationView.as_view(), name='room-moderate'),
    path('<str:room_id>/end/', EndRoomView.as_view(), name='room-end'),
]
