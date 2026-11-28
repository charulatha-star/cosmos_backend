from django.contrib import admin
from .models import Space, SpaceMember, SpaceInvitation, GuestRoomAccessRequest

class SpaceMemberInline(admin.TabularInline):
    model = SpaceMember
    extra = 1

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'team_size', 'allow_link_join', 'created_at')
    search_fields = ('id', 'name', 'owner__email', 'owner__name')
    list_filter = ('allow_link_join', 'created_at')
    inlines = [SpaceMemberInline]

@admin.register(SpaceMember)
class SpaceMemberAdmin(admin.ModelAdmin):
    list_display = ('space', 'user', 'guest_name', 'role', 'access', 'created_at')
    list_filter = ('role', 'access', 'space')
    search_fields = ('space__name', 'user__email', 'user__name', 'guest_name')

@admin.register(SpaceInvitation)
class SpaceInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'space', 'role', 'status', 'invited_by', 'created_at')
    list_filter = ('status', 'role')
    search_fields = ('email', 'space__name')

@admin.register(GuestRoomAccessRequest)
class GuestRoomAccessRequestAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'space', 'requested_room_name', 'status', 'created_at')
    list_filter = ('status', 'space')
    search_fields = ('guest_name', 'space__name', 'requested_room_name')

