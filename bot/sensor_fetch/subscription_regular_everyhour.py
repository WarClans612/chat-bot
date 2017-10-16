import sys
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot")
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot/bot")
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot/fb_api")
from bot import bot_config
import mongodb as M
import send_request as send
import bot_function as BOT
mapping = {"WEATHER": "天氣" , "RAIN": "降雨" , "PM25": "PM2.5" ,"GOOUT": "戶外資訊" ,"UVI": "紫外線指數"}

def get_users(handle_code):
	mongo_client, db, collect = M.open_connection()
	user_id_list = M.find_user_subscribed(collect, handle_code)
	user_list = []
	for user_id in user_id_list:
		user = {}
		user["user_id"] = user_id
		user["space"] = M.get_subscribe_space(collect,user_id,handle_code)	
		user_list.append(user)
	M.close_connection(mongo_client)
	return user_list
	
def get_pushed_user(tag):
	pushed_user_id_list = []
	mongo_client, db, collect = M.open_connection()
	pushed_user_id_list = M.get_pushed_user(db, tag)
	M.close_connection(mongo_client)
	return pushed_user_id_list
	
def save_pushed_user(tag,pushed_user_id_list):
	mongo_client, db, collect = M.open_connection()
	pushed_user_list = []
	for user_id in pushed_user_id_list:
		user = {}
		user["user_id"] = user_id
		user["tag"] = tag
		pushed_user_list.append(user)
	M.save_pushed_user(db, pushed_user_list)
	M.close_connection(mongo_client)
	
def push_notice(handle_code,user_list,pushed_user_id_list):
	mongo_client, db, collect = M.open_connection()
	for user in user_list:
		if user["user_id"] not in pushed_user_id_list:
			slots = {}
			slots["time"] = "now"
			slots["space"] = user["space"]
			answer = BOT.sensor_handler_for_subscription(handle_code,slots)
			if answer != None:
				text = "[訂閱-"+mapping[handle_code]+"]"+answer
				send.send_text(user["user_id"], text)
				pushed_user_id_list.append(user["user_id"])
		
	
	
if __name__ == "__main__" :
	handle_list = ["PM25","UVI"]
	for handle_code in handle_list:
		pushed_user_id_list = get_pushed_user(handle_code)
		user_list = get_users(handle_code)
		push_notice(handle_code,user_list,pushed_user_id_list)
		save_pushed_user(handle_code,pushed_user_id_list)
		
		
		
	