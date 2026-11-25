import uuid
import secrets
import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone

class Space(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=150)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spaces')
    admin_access = models.BooleanField(default=True)
    is_free = models.BooleanField(default=True)
    team_size = models.CharField(max_length=20, default='< 20')
    style = models.CharField(max_length=20, default='minimal')
    allow_link_join = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=64, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = str(uuid.uuid4()).replace('-', '')[:16]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.id})"


class SpaceMember(models.Model):
    ROLE_CHOICES = (
        ('Owner', 'Primary Owner'),
        ('Admin', 'Admin'),
        ('Member', 'Member'),
        ('Guest', 'Guest'),
    )
    ACCESS_CHOICES = (
        ('all_offices', 'All offices'),
        ('specific_room', 'Specific room'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='space_memberships', null=True, blank=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    access = models.CharField(max_length=50, choices=ACCESS_CHOICES, default='all_offices')
    allowed_rooms = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('space', 'user')

    def __str__(self):
        name = self.user.name if self.user else (self.guest_name or 'Guest')
        return f"{name} in {self.space.name} ({self.role})"


class GuestRoomAccessRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved_room', 'Approved Room'),
        ('approved_all', 'Approved All'),
        ('rejected', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='guest_access_requests')
    guest_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='guest_access_requests')
    guest_name = models.CharField(max_length=255)
    requested_room = models.CharField(max_length=100)
    requested_room_name = models.CharField(max_length=150)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    responded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_guest_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guest_name} request for {self.requested_room_name} ({self.status})"


class SpaceInvitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    )
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Member', 'Member'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Member')
    token = models.CharField(max_length=64, unique=True, blank=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(days=7)
        super().save(*args, **kwargs)

    def is_valid(self):
        if self.status != 'pending':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        return True

    def __str__(self):
        return f"Invite for {self.email} to {self.space.name} ({self.role}) [{self.status}]"

class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='temporary')
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type}) - Cap: {self.capacity}"
