from channels.generic.websocket import AsyncWebsocketConsumer
from chat import services
import json
from channels.layers import get_channel_layer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"] or 0)

        if not self.user.is_authenticated or not self.other_user_id:
            await self.close()
            return

        ids = sorted([self.user.id, self.other_user_id])
        self.room_name = f"chat_{ids[0]}_{ids[1]}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        self.chat_open = True

        # Send all messages as chat_history to the opening user
        # all_messages = await services.get_messages(self.user.id, self.other_user_id)
        # await self.send(text_data=json.dumps({
        #     "type": "chat_history",
        #     "messages": all_messages
        # }))

        # Mark unread messages as read and broadcast read receipts
        read_ids = await services.mark_messages_as_read(self.user, self.other_user_id)
        for msg_id in read_ids:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "message_read",
                    "message_id": msg_id
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        self.chat_open = False

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type", "chat_message")

        if event_type == "chat_open":
            self.chat_open = True
            # mark unread messages as read and broadcast
            read_ids = await services.mark_messages_as_read(self.user, self.other_user_id)
            for msg_id in read_ids:
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        "type": "message_read",
                        "message_id": msg_id
                    }
                )
            return

        if event_type == "chat_close":
            self.chat_open = False
            return
        
        if event_type == "delete_message":
            message_id = data.get("message_id")
            if message_id:
                deleted = await services.delete_message(self.user, message_id)
                if deleted:
                    # Notify everyone in the room to remove the message
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            "type": "message_deleted",
                            "message_id": message_id
                        }
                    )
                    # Notify the other user about updated unread count
                    count = await services.get_unread_count_for_conversation(self.other_user_id, self.user.id)
                    await self.channel_layer.group_send(
                        f"user_{self.other_user_id}_notifications",
                        {
                            "type": "unread_update",
                            "user_id": self.user.id,  # this conversation is with sender
                            "count": count
                        }
                    )
            return

        if data.get("type") == "typing":
            await self.channel_layer.group_send(
                self.room_name,  # use self.room_name
                {
                    "type": "user_typing",
                    "user_id": self.user.id,
                    "is_typing": data["is_typing"]
                }
            )
            return  

        # Normal chat message
        message_text = data.get("message")
        if not message_text:
            return

        message = await services.create_message(self.user, self.other_user_id, message_text)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message_id": message.id,
                "message": message.content,
                "sender": self.user.username,
                "is_read": message.is_read,
            }
        )

        # Notify the other user about updated unread count
        count = await services.get_unread_count_for_conversation(self.other_user_id, self.user.id)
        await self.channel_layer.group_send(
            f"user_{self.other_user_id}_notifications",
            {
                "type": "unread_update",
                "user_id": self.user.id,  # this conversation is with sender
                "count": count
            }
        )

    # Send a new chat message to WebSocket
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # Send a read receipt to WebSocket
    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            "type": "read_receipt",
            "message_id": event["message_id"]
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            "type": "message_deleted",
            "message_id": event["message_id"]
        }))

    # Send typing info to WebSocket
    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "is_typing": event["is_typing"]
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add("status_group", self.channel_name)
        await self.accept()

        # Send initial unread counts
        unread_counts = await services.get_unread_counts(self.user)
        await self.send(text_data=json.dumps({
            "type": "unread_counts",
            "counts": unread_counts
        }))

        # Notify all users this user is online
        await self.channel_layer.group_send(
            "status_group",
            {
                "type": "user_status",
                "user_id": self.user.id,
                "is_online": True
            }
        )

    async def disconnect(self, close_code):
        # Remove from groups only, do NOT mark offline
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard("status_group", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "user_logout":
            # Remove user from groups and notify others
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.channel_layer.group_discard("status_group", self.channel_name)
            await self.channel_layer.group_send(
                "status_group",
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "is_online": False
                }
            )
            await self.close()  # Close the WebSocket

    # Receive unread count update
    async def unread_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_update",
            "user_id": event["user_id"],
            "count": event["count"]
        }))

    # Receive online/offline status update
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_status",
            "user_id": event["user_id"],
            "is_online": event["is_online"]
        }))