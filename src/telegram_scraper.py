import os
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message

# Load environment variables once
os.environ.clear()
load_dotenv(override=True)

TELEGRAM_APP_ID = os.environ.get('telegram_app_id')
TELEGRAM_API_HASH = os.environ.get("telegram_api_hash")

# --- 2. Helper Functions ---

def get_channel_identifier(channel_url: str) -> str:
    """Extracts the channel username or identifier from a URL or string."""
    if "t.me/" in channel_url:
        return urlparse(channel_url).path.lstrip('/')
    return channel_url.lstrip('@')

def get_data_lake_paths(base_path: Path, channel_identifier: str, msg_date: datetime):
    """
    Generates the partitioned directory structure for storing raw data.
    Example: data/raw/telegram_messages/YYYY-MM-DD/channel_name.json
    """
    date_str = msg_date.strftime("%Y-%m-%d")
    
    # Path for JSON data
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, 'data', 'raw', 'telegram_messages' , date_str)
    json_path.mkdir(parents=True, exist_ok=True)
    json_file = json_path / f"{channel_identifier}.jsonl" # Using .jsonl for line-delimited JSON

    # Path for images
    image_path = base_path / "raw" / "images" / date_str / channel_identifier
    image_path.mkdir(parents=True, exist_ok=True)
    
    return json_file, image_path

# --- 3. Core Scraping Logic ---

async def scrape_channel(client: TelegramClient, channel_url: str, base_data_path: Path):
    """
    Scrapes a single Telegram channel, saving messages to the data lake and downloading images.
    """
    channel_identifier = get_channel_identifier(channel_url)
    print(f"Starting to scrape channel: {channel_identifier}")

    try:
        entity = await client.get_entity(channel_identifier)
    except Exception as e:
        print(f"Could not get entity for '{channel_identifier}'. Error: {e}")
        return

    messages_scraped_count = 0
    async for message in client.iter_messages(entity, limit=200): # Limit can be adjusted
        if not isinstance(message, Message):
            continue

        # Get paths for storing data in the data lake
        json_file, image_path = get_data_lake_paths(base_data_path, channel_identifier, message.date)
        
        # a) Store raw, unaltered data as JSON, preserving the original structure 
        try:
            with open(json_file, 'a', encoding='utf-8') as f:
                # Convert the Telethon message object to a dictionary and write as a JSON line
                message_dict = message.to_dict()
                f.write(json.dumps(message_dict, default=str) + '\n')
            messages_scraped_count += 1
        except Exception as e:
            print(f"Failed to write message {message.id} to {json_file}. Error: {e}")

        # b) Collect images for object detection 
        if message.photo:
            try:
                # Download media to the structured image directory
                photo_path = await client.download_media(message.photo, file=image_path)
                print(f"Saved image from message {message.id} to {photo_path}")
            except Exception as e:
                print(f"Failed to download photo from message {message.id}. Error: {e}")

    print(f"Finished scraping {channel_identifier}. Scraped {messages_scraped_count} messages.")


# --- 4. Main Execution ---

async def main():
    """
    Main function to initialize the client and orchestrate the scraping of all channels.
    """
    # Define the absolute path to the project's root directory
    # This makes the script runnable from anywhere
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_lake_base_path = project_root / "data"

    print(f"Data lake will be populated at: {data_lake_base_path.absolute()}")

    # List of channels to scrape
    channels_to_scrape = [
        "https://t.me/lobelia4cosmetics",
        "https://t.me/tikvahpharma",
        # You can add more from https://et.tgstat.com/medicine [cite: 78]
    ]

    async with TelegramClient('scraping_session', TELEGRAM_APP_ID, TELEGRAM_API_HASH) as client:
        print("Telegram client started.")
        tasks = []
        for channel in channels_to_scrape:
            # Create a scraping task for each channel
            task = scrape_channel(client, channel, data_lake_base_path)
            tasks.append(task)
        
        # Run all scraping tasks concurrently
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Ensure credentials are set
    if not TELEGRAM_APP_ID or not TELEGRAM_API_HASH:
        print("FATAL ERROR: 'telegram_app_id' and 'telegram_api_hash' not found in environment variables.")
        print("Please create a .env file and add your Telegram credentials.")
    else:
        # Run the main asynchronous function
        asyncio.run(main())