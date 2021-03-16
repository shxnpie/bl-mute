import dill
from telethon.tl import types

from userbot import client
from userbot.utils.events import NewMessage

plugin_category = "riyazgay"
redis = client.database
dbKey = "autodelete:users"
hashmap = {}  # {chat: [id0, id1, idn]}

if redis:
    if redis.exists(dbKey):
        hashmap.update(dill.loads(redis.get(dbKey)))


async def update_db() -> None:
    if redis:
        if hashmap:
            redis.set(dbKey, dill.dumps(hashmap))
        else:
            redis.delete(dbKey)

@client.onMessage(require_admin=True, incoming=True)
async def _incoming_listner(event: NewMessage.Event) -> None:
    if (
        event.chat_id not in hashmap and
        (event.is_channel or event.is_private) and
        not (event.chat.creator or event.chat.admin_rights.delete_messages)
    ):
        return

    if event.sender_id in hashmap[event.chat_id]:
        await event.delete()


async def get_users(event: NewMessage.Event) -> types.User or None:
    match = event.matches[0].group(1)
    users = []
    if match:
        matches, _ = await client.parse_arguments(match)
        for match in matches:
            try:
                entity = await client.get_entity(match)
                if isinstance(entity, types.User):
                    users.append(entity.id)
            except (TypeError, ValueError):
                pass
    elif event.is_private and event.out:
        users = [await event.get_chat().id]
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        users = [await reply.get_sender().id]
    return users


@client.onMessage(
    command=("ad", plugin_category),
    outgoing=True, regex=r"ad(?: |$)(.+)?$"
)
async def autodel(event: NewMessage.Event) -> None:
    if not redis:
        await event.answer("DB not found.")
        return
    users = await get_users(event)
    hashmap.setdefault(event.chat_id, set()).update(users)
    await event.edit("`Updated DB`")


@client.onMessage(
    command=("rmad", plugin_category),
    outgoing=True, regex=r"rmad(?: |$)(.+)?$"
)
async def rmautodel(event: NewMessage.Event) -> None:
    if not redis:
        await event.answer("DB not found.")
        return
    users = await get_users(event)
    hashmap.setdefault(event.chat_id, set()).difference_update(users)
    await event.edit("`Updated DB`")
