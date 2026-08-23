import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('config.env')

BASE_DIR = Path(__file__).parent.absolute()

TG_TOKEN = os.getenv('TG_TOKEN')
if not TG_TOKEN:
    raise ValueError("TG_TOKEN не задан в config.env")

VK_TOKEN = os.getenv('VK_TOKEN')
if not VK_TOKEN:
    raise ValueError("VK_TOKEN не задан в config.env")

# VK_TOKEN = os.getenv('PROXY')
# if not VK_TOKEN:
#     raise ValueError("PROXY не задан в config.env")

ADMIN_KEY = os.getenv('ADMIN_KEY')
SQLALCHEMY_URL = os.getenv('SQLALCHEMY_URL', 'sqlite+aiosqlite:///./database.db')
DEEPSEEK_API = os.getenv('DEEPSEEK_API')

PATH_TO_IMAGES = os.getenv('PATH_TO_IMAGES', 'app/assets/menu/')
PATH_TO_NAMING = os.getenv('PATH_TO_NAMING', 'app/assets/texts/names.json')
PATH_TO_LOGS = os.getenv('PATH_TO_LOGS', 'app/components/logs/')
