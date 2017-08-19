import process
import send_request as send
import mongodb as M
from pymessager.message import Messager
from pymessager.message import QuickReply
from pymessager.message import ContentType

def push_notice(sub_tag,text):
	mongo_client, db, collect = M.open_connection()
	
	user_list = M.find_user_subscribed(collect, sub_tag)
	for user_id in user_list:
		send.send_text(user_id, text)
	
	M.close_connection(mongo_client)
	
if __name__ == "__main__" :
	text = "現在PM25很高 空氣品質不好 外出請注意!"
	push_notice("PM25",text)
	