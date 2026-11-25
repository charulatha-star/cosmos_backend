from rest_framework import serializers
from .models import Room, Space, SpaceMember, SpaceInvitation, GuestRoomAccessRequest

class SpaceMemberSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = SpaceMember
        fields = [
            'id',
            'space',
            'user',
            'name',
            'email',
            'guest_name',
            'role',
            'access',
            'allowed_rooms',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_name(self, obj):
        if obj.user:
            return obj.user.name or obj.user.email.split('@')[0]
        return obj.guest_name or 'Guest'

    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return None


class GuestRoomAccessRequestSerializer(serializers.ModelSerializer):
    guest_email = serializers.ReadOnlyField(source='guest_user.email')
    responded_by_name = serializers.ReadOnlyField(source='responded_by.name')

    class Meta:
        model = GuestRoomAccessRequest
        fields = [
            'id',
            'space',
            'guest_user',
            'guest_name',
            'guest_email',
            'requested_room',
            'requested_room_name',
            'status',
            'responded_by',
            'responded_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'responded_by', 'created_at', 'updated_at']


class SpaceInvitationSerializer(serializers.ModelSerializer):
    invited_by_name = serializers.ReadOnlyField(source='invited_by.name')
    space_name = serializers.ReadOnlyField(source='space.name')

    class Meta:
        model = SpaceInvitation
        fields = [
            'id',
            'space',
            'space_name',
            'email',
            'role',
            'token',
            'invited_by',
            'invited_by_name',
            'status',
            'expires_at',
            'created_at',
        ]
        read_only_fields = ['id', 'token', 'status', 'expires_at', 'created_at']



class SpaceSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.name')
    owner_email = serializers.ReadOnlyField(source='owner.email')
    members_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = [
            'id',
            'name',
            'owner',
            'owner_name',
            'owner_email',
            'admin_access',
            'is_free',
            'team_size',
            'style',
            'allow_link_join',
            'invite_code',
            'members_count',
            'user_role',
            'is_admin',
            'created_at',
        ]
        read_only_fields = ['id', 'owner', 'invite_code', 'created_at']

    def get_members_count(self, obj):
        return obj.members.count()

    def get_user_role(self, obj):
        request = self.context.get('request')
        if not request or not getattr(request, 'user', None) or not request.user.is_authenticated:
            return 'Guest'
        if obj.owner == request.user or (obj.owner_id and obj.owner_id == request.user.id):
            return 'Owner'
        member = SpaceMember.objects.filter(space=obj, user=request.user).first()
        if member:
            return member.role
        return 'Member'

    def get_is_admin(self, obj):
        role = self.get_user_role(obj)
        return role in ['Owner', 'Admin']


class RoomSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    active_participants = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'type',
            'capacity',
            'description',
            'created_by',
            'created_by_name',
            'active_participants',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_active_participants(self, obj):
        # Can be dynamically populated from LiveKit or cache
        return []

    def validate(self, attrs):
        request = self.context.get('request')
        room_type = attrs.get('type', 'temporary')

        # PRD Section 3 rule: Only Admins can create permanent rooms
        if room_type == 'permanent' and request and request.user.role != 'Admin':
            raise serializers.ValidationError({"type": "Only Admins can create permanent rooms."})

        return attrs
