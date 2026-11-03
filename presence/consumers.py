import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class OfficePresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = "office_main"

        # Join the global office group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Broadcast that this user came online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status_update",
                "user_id": str(self.user.id),
                "name": self.user.name,
                "status": "online",
            }
        )

    async def disconnect(self, close_code):
        # Leave office group and mark user offline
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status_update",
                "user_id": str(self.user.id),
                "status": "offline",
            }
        )

    # Receive avatar movement coordinates from browser
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "avatar_move":
            x = data.get("x")
            y = data.get("y")
            desk = data.get("desk")

            # Cache the latest position in Redis
            cache.set(f"user_pos_{self.user.id}", {"x": x, "y": y, "desk": desk}, timeout=3600)

            # Broadcast coordinates to all teammates in the office
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "avatar_moved",
                    "user_id": str(self.user.id),
                    "name": self.user.name,
                    "x": x,
                    "y": y,
                    "desk": desk,
                }
            )

    async def avatar_moved(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_status_update(self, event):
        await self.send(text_data=json.dumps(event))