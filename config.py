from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.environ.get('API_ID', ''))
API_HASH = os.environ.get('API_HASH', '')
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_KEY = os.getenv("DATABASE_KEY")
LOG_ID = int(os.environ.get('LOG_CHAT_ID', ''))
TABLE_NAME = os.getenv("TABLE_NAME")
DRIVE_ID = int(os.environ.get('DRIVE_ID', ''))
