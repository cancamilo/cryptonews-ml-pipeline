import os
import asyncio
from telethon.sync import TelegramClient
from config import settings

dir_path = os.path.dirname(os.path.realpath(__file__))
session_path = os.path.join(dir_path, "session_data")

# Execute this code to initialize a telegram session.
# The first time it will prompt youy to enter your phone number and a code to sign in.
async def init_client():
    async with TelegramClient(f'{session_path}/my_user', settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH) as client:
        user = await client.get_me()
        print(f"Hello {user.first_name} {user.last_name}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_client())
    print(f"session file saved to {session_path}")
