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