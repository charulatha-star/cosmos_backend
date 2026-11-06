from django.urls import path
from .views import PresenceListView, PresenceUpdateView

urlpatterns = [
    path('', PresenceListView.as_view(), name='presence-list'),
    path('update/', PresenceUpdateView.as_view(), name='presence-update'),
]
