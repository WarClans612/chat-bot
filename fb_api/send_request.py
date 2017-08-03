import json
from pymessager.message import Messager
from pymessager.message import QuickReply
from pymessager.message import ContentType

from fb_api_config import facebook_access_token 

def query_location(user_id):
	client = Messager(facebook_access_token)
	text = "請告訴我您的地點"
	reply_list = [QuickReply(content_type=ContentType.LOCATION)]
	client.send_quick_replies(user_id, text, reply_list)
	
def send_text(user_id, text):
	client = Messager(facebook_access_token)
	client.send_text(user_id, text)
	
	
def hello_to_new_user(user_id):
	text = "歡迎使用台灣生活品質小幫手\
			可以詢問我關於天氣或空氣品質等等的問題喔^^\
			"
	client = Messager(facebook_access_token)
	client.send_text(user_id, text)
	
def say_something(user_id):
	text = "我還小聽不懂> <\
			可以問我天氣或空氣品質的問題唷~"
	client = Messager(facebook_access_token)
	client.send_text(user_id, text)