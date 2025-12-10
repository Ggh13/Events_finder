import asyncio
import os
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import json
from datetime import datetime
from pathlib import Path
import config

class TelegramParser:
    def __init__(self, api_id: str, api_hash: str, phone: str) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.cnt = 0

        self.client = TelegramClient('session', api_id=api_id, api_hash=api_hash)

    async def start(self):
        await self.client.start(self.phone)

    async def parse_channel(self, channel_username: str, limit: int = 100) -> None:
        try:
            channel_info = await self.client.get_entity(channel_username)

            channel_dir = os.path.join(self.data_dir, channel_username.replace('@', ''))
            images_dir = os.path.join(channel_dir, 'images')
            os.makedirs(images_dir, exist_ok=True)

            posts_data = []

            async for message in self.client.iter_messages(channel_info, limit=limit):
                if len(posts_data) >= 200:
                    break
                
                post_info = await self._proccess_message(message, images_dir)
                if post_info:
                    posts_data.append(post_info)

            await self._save_posts_data(channel_dir, channel_info, posts_data)
            return
        except Exception as e:
            print(f"Error! : {e}")
    
    async def _proccess_message(self, message: str, img_dir: Path) -> dict:
        if not message.message or message.message == '': return None

        post_info = {
            'id': message.id,
            'text': message.message,
            'has_image': False,
            'img_filename': None
        }

        if message.media and isinstance(message.media, MessageMediaPhoto):
            try:
                timestamp = int(datetime.now().timestamp())
                filename = f"{message.id}_{timestamp}.jpg"
                filepath = os.path.join(img_dir, filename)
                await self.client.download_media(message.media, file=str(filepath))
                post_info['img_filename'] = filename
                post_info['has_image'] = True
            
            except Exception as e:
                print(f'Error! : {e}')

        return post_info
    
    async def _save_posts_data(self, channel_dir: Path, channel: str, posts_data: list[dict]) -> None:
        save_data = {
            'username': channel.username,
            'posts': posts_data
        }

        json_path = os.path.join(channel_dir, 'posts.json')
        with open (json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False)
    
    async def close(self) -> None:
        await self.client.disconnect()
    

async def main():
    parser = TelegramParser(
        api_id=config.api_id,
        api_hash=config.api_hash, 
        phone=config.phone
    )
    await parser.start()
    for channel in config.channels:
        channel_us = channel["username"]
        await parser.parse_channel(channel_us, limit=config.limit)
        await asyncio.sleep(5)
    await parser.close()

if __name__ == "__main__":
    asyncio.run(main())        