"""
Script to upload a sticker pack to Telegram.
"""
import asyncio
import json
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.messages import GetAllStickersRequest, GetStickerSetRequest
from telethon.tl.types import InputStickerSetID
from telethon.utils import pack_bot_file_id

IMAGES_DIR = Path(__file__).resolve().parent
SESSION_NAME = "sticker_uploader"

COLORS = ["r", "g", "b", "y"]
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "draw", "reverse", "skip"]
SPECIALS = ["colorchooser", "draw_four"]

# Create this config file by copying the example file
with open(IMAGES_DIR / "sticker_config.json", "r", encoding="utf-8") as f:
    sticker_config = json.load(f)

STICKERS_DIR = IMAGES_DIR / sticker_config["sticker_dir"]

# You must get your own api_id and api_hash from https://my.telegram.org,
# under API Development, and put them into a file called "api_auth.json"
with open(IMAGES_DIR / "api_auth.json", "r", encoding="utf-8") as f:
    api_auth = json.load(f)

api_id = api_auth["api_id"]
api_hash = api_auth["api_hash"]

# Load the session from disk, or create a new one if it doesn't exist
session_file = IMAGES_DIR / f"{SESSION_NAME}.session"
session = str(session_file.absolute())

# Create the client and connect
client = TelegramClient(
    session,
    api_id,
    api_hash,
    receive_updates=False,
)
client.start()


async def delete_if_existing(stickers_bot):
    sticker_sets = await client(GetAllStickersRequest(0))

    for s in sticker_sets.sets:
        if s.short_name == sticker_config["pack_name"]:
            print(f'Deleting existing sticker set "{s.short_name}" ({s.id})')
            await client.send_message(stickers_bot, "/delpack")
            await client.send_message(stickers_bot, s.short_name)
            break


async def create_sticker_set(stickers_bot):
    """
    Create a new sticker set by conversing with @Stickers.
    """
    await client.send_message(stickers_bot, "/newpack")
    await client.send_message(stickers_bot, sticker_config["pack_name"])


async def get_sticker_set():
    """
    Get the sticker set that we just created.
    """
    sticker_sets = await client(GetAllStickersRequest(0))

    for s in sticker_sets.sets:
        if s.short_name == sticker_config["pack_name"]:
            sticker_set_ref = s
            break
    else:
        raise Exception(f'Could not find sticker set "{sticker_config["pack_name"]}"')

    sticker_set = await client(
        GetStickerSetRequest(
            InputStickerSetID(id=sticker_set_ref.id, access_hash=sticker_set_ref.access_hash),
            hash=0,
        )
    )
    return sticker_set


async def get_sticker_ids(sticker_set):
    """
    Get the sticker file IDs of the stickers in the given sticker set, mapped to their sticker ID.
    """
    sticker_ids = []

    for special in SPECIALS:
        sticker_ids.append(special)

    for color in COLORS:
        for number in NUMBERS:
            sticker_ids.append(
                f"{color}_{number}",
            )

    stickers = {}

    for sticker_id, document in zip(sticker_ids, sticker_set.documents):
        file_id = pack_bot_file_id(document)
        stickers[sticker_id] = file_id

    return stickers


async def save_sticker_ids():
    # Get the sticker ids
    sticker_set = await get_sticker_set()
    stickers = await get_sticker_ids(sticker_set)

    # Save the stickers to a file
    with open(IMAGES_DIR / f"sticker_ids_{sticker_config['pack_name']}.json", "w") as f:
        json.dump(stickers, f, indent=4)


async def upload_sticker(entity, sticker_path):
    """
    Uploads a sticker to the current conversation.
    """
    message = await client.send_file(
        entity,
        sticker_path,
        force_document=True,
    )
    await client.send_message(entity, sticker_config["sticker_emoji"])
    return message


async def main():
    me = await client.get_me()
    print(f"Logged in as {me.username} ({me.id})")

    BOT_USERNAME = "Stickers"
    stickers_bot = await client.get_entity(BOT_USERNAME)

    ### Uncomment if you missed the prompt to add the sticker pack to your account ###
    # await save_sticker_ids()
    # return

    # Delete the existing sticker set if it exists
    await delete_if_existing(stickers_bot)
    await asyncio.sleep(1)

    # Create a new sticker set
    await create_sticker_set(stickers_bot)

    # Upload the stickers
    async def do_sticker_upload(path):
        await upload_sticker(stickers_bot, path)
        await asyncio.sleep(1)

    for special in SPECIALS:
        await do_sticker_upload(
            STICKERS_DIR / f"{special}.webp",
        )

    for color in COLORS:
        for number in NUMBERS:
            await do_sticker_upload(
                STICKERS_DIR / f"{color}_{number}.webp",
            )

    await client.send_message(stickers_bot, "/publish")
    await client.send_message(stickers_bot, "/skip")
    await client.send_message(stickers_bot, sticker_config["pack_name"])

    # Wait for the user to add the sticker pack to their account
    print("Please add the sticker pack to your account by clicking the link posted by @Stickers")
    print(f"https://t.me/addstickers/{sticker_config['pack_name']}")
    await asyncio.sleep(10)

    # Save the sticker IDs to a file
    await save_sticker_ids()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
