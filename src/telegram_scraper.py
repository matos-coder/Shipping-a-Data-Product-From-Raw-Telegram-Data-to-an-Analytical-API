import os
import sys
from dotenv import load_dotenv
import asyncio
from telethon import TelegramClient
import csv

# Load environment variables once
os.environ.clear()
load_dotenv(override=True)

TELEGRAM_APP_ID = os.environ.get('telegram_app_id')
TELEGRAM_API_HASH = os.environ.get("telegram_api_hash")

# Function to scrape data from a single channel
async def scrape_channel(client, channel_username, writer, media_dir):
    print(f"Starting to scrape {channel_username}")
    entity = await client.get_entity(channel_username)
    print(f"Got entity for {channel_username}")
    channel_title = entity.title  # Extract the channel's title
    async for message in client.iter_messages(entity, limit=1000):
        media_path = None
        if message.media and hasattr(message.media, 'photo'):
            # Create a unique filename for the photo
            filename = f"{channel_username}_{message.id}.jpg"
            media_path = os.path.join(media_dir, filename)
            # Download the media to the specified directory if it's a photo
            await client.download_media(message.media, media_path)
        
        # Get view count (may be None if not available)
        view_count = getattr(message, 'views', None)
        
        # Write the channel title along with other data
        writer.writerow([channel_title, channel_username, message.id, message.message, message.date, media_path, view_count])
        pass
    print(f"Finished scraping {channel_username}")