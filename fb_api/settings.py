import sys
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot")
from bot import bot_config

MONGO_HOST = bot_config.db_url
MONGO_PORT = 27017
MONGO_DBNAME = bot_config.db_name
TABLE_NAME = 'user_information'

