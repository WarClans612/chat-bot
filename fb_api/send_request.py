import json
from fb_api.pymessager.message import Messager
from fb_api.pymessager.message import QuickReply
from fb_api.pymessager.message import ContentType
from fb_api.fb_config import ACCESS_TOKEN
import random
 
mapping = {"WEATHER": "天氣" , "RAIN": "降雨" , "PM25": "PM2.5" ,"GOOUT": "戶外資訊" ,"UVI": "紫外線指數"}

def query_location(user_id):
    client = Messager(ACCESS_TOKEN)
    text = "請告訴我您的地點"
    reply_list = [QuickReply(content_type=ContentType.LOCATION)]
    client.send_quick_replies(user_id, text, reply_list)

def query_subscription_location(user_id):
    client = Messager(ACCESS_TOKEN)
    text = "請告訴我您想訂閱的地點"
    reply_list = [QuickReply(content_type=ContentType.LOCATION)]
    button = QuickReply("取消", "SET_DEFAULT")
    reply_list.append(button)
    client.send_quick_replies(user_id, text, reply_list)

def send_text(user_id, text):
    client = Messager(ACCESS_TOKEN)
    client.send_text(user_id, text)

def hello_to_new_user(user_id):
    text = "歡迎使用台灣生活品質小幫手\
            可以詢問我關於天氣或空氣品質等等的問題喔^^\
            "
    client = Messager(ACCESS_TOKEN)
    client.send_text(user_id, text)
    
def say_something(user_id):
    text_list = [
        "可以問我天氣或空氣品質的問題唷~",
        "可以問我天氣或是紫外線指數狀況喔!",
        "跟我訂閱資訊,可以即時通知喔~",
        "快來跟我訂閱資訊,讓你出門不煩惱",
        "有什麼建議可以在粉專上面留言給我媽咪唷~",
        ]
    num = random.randint(0,len(text_list)-1)
    text = "我還小聽不懂> <  " + text_list[num]
    client = Messager(ACCESS_TOKEN)
    client.send_text(user_id, text)
    
def send_sQA_answer(user_id,answer,button_list):
    client = Messager(ACCESS_TOKEN)
    if len(button_list) == 0:
        client.send_text(user_id, answer)
    else:
        client.send_quick_replies(user_id, answer, button_list)
        
def send_subscribe_mess(user_id, TF, tag, space):
    client = Messager(ACCESS_TOKEN)
    if TF == True:
        if tag in ["WEATHER","RAIN","GOOUT"]:
            text = "已經幫您訂閱"+space+"的"+mapping[tag]+", 將會在每天早上通知喔!"
        elif tag in ["PM25","UVI"]:
            text = "已經幫您訂閱"+space+"的"+mapping[tag]+", 只會在數值過量時通知喔!"
        else:
            print("[ERR] no this type of tag")
            text = "已經幫您訂閱"+space+"的"+mapping[tag]
    else:
        text = "好的,若需要訂閱相關資訊再告訴我[訂閱]喔"
    client.send_text(user_id, text)

def send_subscribe_ask(user_id,tag,space):
    text = "確定要訂閱"+space+"的"+mapping[tag]+"嗎?"
    
    button_list = []
    button = QuickReply("沒錯","_FUN=SUBYES_TAG="+tag+"_LOC="+space+"_")
    button_list.append(button)
    button = QuickReply("我想要訂閱別的縣市", "_FUN=SUBOTHER_TAG="+tag+"_")
    button_list.append(button)

    send_button_list(user_id,text,button_list)
    
def send_sublist(user_id, other_list):
    if len(other_list) == 0:
        text = "你都已經訂閱囉^^"
        send_button_list(user_id, text, [])
    else:
        text = "想訂閱什麼呢?"
        button_list = []
        for tag in other_list:
            button = QuickReply("訂閱"+mapping[tag],"_FUN=SUB_TAG="+tag+"_")
            button_list.append(button)
        send_button_list(user_id, text, button_list)
        
def send_unsublist(user_id, subscirbed_list):
    if len(subscirbed_list) == 0:
        text = "你目前沒有訂閱喔,可以告訴我[訂閱]來查看有哪些項目"
        send_button_list(user_id, text, [])
    else:
        text = "想取消什麼呢?"
        button_list = []
        for tag in subscirbed_list:
            button = QuickReply("取消訂閱"+mapping[tag],"_FUN=UNSUB_TAG="+tag+"_")
            button_list.append(button)
        send_button_list(user_id, text, button_list)

def send_cancel(user_id):
    client = Messager(ACCESS_TOKEN)
    text = "好的,若需要訂閱相關資訊再告訴我[訂閱]喔"
    client.send_text(user_id, text)
    
def send_button_list(user_id,text,button_list):
    client = Messager(ACCESS_TOKEN)
    if len(button_list) == 0:
        client.send_text(user_id, text)
    else:
        client.send_quick_replies(user_id, text, button_list)
