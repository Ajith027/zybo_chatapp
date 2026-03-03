from asgiref.sync import sync_to_async

@sync_to_async
def create_message(sender, receiver_id, content):
    from .models import Message

    return Message.objects.create(
        sender=sender,
        receiver_id=receiver_id,
        content=content
    )

@sync_to_async
def mark_messages_as_read(user, other_user_id):
    from .models import Message

    unread = Message.objects.filter(
        sender_id=other_user_id,
        receiver=user,
        is_read=False
    )
    unread_ids = list(unread.values_list('id', flat=True))
    unread.update(is_read=True)
    return unread_ids

@sync_to_async
def get_messages(user1_id, user2_id):
    from .models import Message

    messages = Message.objects.filter(
        sender_id__in=[user1_id, user2_id],
        receiver_id__in=[user1_id, user2_id],
        is_deleted=False
    ).order_by("timestamp")

    return [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "message": msg.content,
            "timestamp": msg.timestamp.strftime("%b %d, %H:%M"),
            "is_read": msg.is_read
        }
        for msg in messages
    ]

@sync_to_async
def delete_message(user, message_id):
    from .models import Message

    """
    Delete a message if the user is the sender.
    Returns True if deleted, False if not found or not authorized.
    """
    try:
        msg = Message.objects.get(id=message_id, sender=user)
        msg.is_deleted =True
        msg.save()
        return True
    except Message.DoesNotExist:
        return False


@sync_to_async
def get_conversations_for_user(user_id):
    from django.contrib.auth import get_user_model
   
    User = get_user_model()
    """
    Return all users that have chatted with this user.
    """
    from .models import Message

    # Users this user sent messages to
    sent_to = Message.objects.filter(
        sender_id=user_id
    ).values_list("receiver_id", flat=True)

    # Users that sent messages to this user
    received_from = Message.objects.filter(
        receiver_id=user_id
    ).values_list("sender_id", flat=True)

    # Combine and remove duplicates
    user_ids = set(list(sent_to) + list(received_from))

    return list(User.objects.filter(id__in=user_ids))

@sync_to_async
def get_unread_count_for_conversation(user_id, other_user_id):
    from .models import Message

    return Message.objects.filter(
        sender_id=other_user_id,
        receiver_id=user_id,
        is_read=False
    ).count()

async def get_unread_counts(user):
    """
    Return a dict {conversation_user_id: unread_count} for all conversations
    """
    counts = {}
    conversations = await get_conversations_for_user(user.id)
    for other_user in conversations:
        count = await get_unread_count_for_conversation(user.id, other_user.id)
        counts[other_user.id] = count
    return counts