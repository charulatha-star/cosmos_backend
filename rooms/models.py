
import uuid
from django.db import models
from django.conf import settings


class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
    )


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='temporary')
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} ({self.type}) - Cap: {self.capacity}"