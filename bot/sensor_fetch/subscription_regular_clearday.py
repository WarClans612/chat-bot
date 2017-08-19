import sys
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot")
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot/bot")
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot/fb_api")
from bot import bot_config
import mongodb as M
import send_request as send
import bot_function as BOT

def clear_pushed_list():
	mongo_client, db, collect = M.open_connection()
	db.subscription_pushed_user.drop()
	M.close_connection(mongo_client)
	
	
if __name__ == "__main__" :
	clear_pushed_list()
		
		
		
	