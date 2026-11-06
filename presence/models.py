from django.db import models
from django.conf import settings

class Presence(models.Model):
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('busy', 'Busy'),
        ('in_room', 'In Room'),
        ('offline', 'Offline'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presence'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='online')
    current_space = models.CharField(max_length=100, default='billion')
    current_desk = models.CharField(max_length=100, blank=True, null=True)
    x = models.IntegerField(default=420)
    y = models.IntegerField(default=580)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} ({self.status}) @ {self.current_desk or f'({self.x},{self.y})'}"
