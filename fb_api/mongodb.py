import pymongo
from pymongo import MongoClient
import datetime as DT
from datetime import datetime
from bot import util as bot_util
from fb_api.fb_config import *
from fb_api.pymessager.message import QuickReply
handle_list = ["WEATHER","RAIN","PM25","GOOUT","UVI"]

#Connect to USER_INFO database
def connect_to_database():
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DBNAME]
    return db
    
#Return collect directly for the USER_INFO table
def connect_user_table():
    db = connect_to_database()
    return db[USER_INFO]

#Check if the user_id exist in the database
def new_user(user_id):
    #Retrieve one random question as initialization
    db = bot_util.connect_to_database()
    collect = db["question_table"]
    init_question = collect.find_one({"handle_code":"WEATHER"})["question_num"]
    
    #Initializes USER_INFO if the ID does not exist
    collect = connect_user_table()
    if collect.find_one({'id':user_id}) is None:
        data = {"id": user_id,
                "state": "default",
                "question_num": init_question,
                "subscription" : {}
            }
        collect.insert_one(data)
        return True
    else:
        return False

def get_state(user_id):
    collect = connect_user_table()
    data = collect.find_one({'id':user_id})
    state = data['state']
    return state
    
def set_state(user_id, state):
    collect = connect_user_table()
    collect.find_one_and_update({'id':user_id},{'$set': {'state':state}})

def save_qnum(user_id, question_num):
    collect = connect_user_table()
    collect.find_one_and_update({'id':user_id},{'$set': {'question_num':question_num}})
    
def save_tag_want_to_subscribe(user_id, tag_want):
    collect = connect_user_table()
    collect.find_one_and_update({'id':user_id},{'$set': {'tag_want':tag_want}})
    
def save_space(user_id, space):
    collect = connect_user_table()
    now_time = datetime.now()
    collect.find_one_and_update({'id':user_id},{'$set': {'space':space, 'space_time':now_time }})

def save_time(user_id, time):
    collect = connect_user_table()
    now_time = datetime.now()
    collect.find_one_and_update({'id':user_id},{'$set': {'time':time, 'time_time':now_time }})
    
def check_space(user_id):
    collect = connect_user_table()
    data = collect.find_one({'id':user_id})
    if data.get("space"):
        now_time = datetime.now()
        ten_mins = DT.timedelta( days=30 )
        if now_time - data["space_time"] < ten_mins:
            return data["space"]
        else:
            return None
    else:
        return None
        
def check_time(user_id):
    collect = connect_user_table()
    data = collect.find_one({'id':user_id})
    if data.get("time"):
        now_time = datetime.now()
        three_mins = DT.timedelta( minutes=3 )
        if now_time - data["time_time"] < three_mins:
            return data["time"]
        else:
            return None
    else:
        return None

def get_data(user_id, Column):
    collect = connect_user_table()
    data = collect.find_one({'id':user_id})[Column]
    return data
    
def get_subscribe_status(user_id, handle_code):
    collect = connect_user_table()
    subscribe_status = collect.find_one({'id':user_id})['subscription']
    if subscribe_status.get(handle_code):
        if subscribe_status[handle_code]:
            return "subscribed"
        else:
            return "never_asked"
    else:
        return "not_asked_yet"
        
def get_subscribe_space(user_id, handle_code):
    collect = connect_user_table()
    item = collect.find_one({'id':user_id})
    subscribe_status = item['subscription']
    if subscribe_status.get(handle_code):
        space = subscribe_status[handle_code+"_space"]
        return space
    else:
        return None
        
def get_all_subscribe_status(user_id):
    collect = connect_user_table()
    subscribe_status = collect.find_one({'id':user_id})['subscription']
    subscribed_list = []
    other_list = handle_list.copy()
    for handle_code in handle_list:
        if subscribe_status.get(handle_code):
            if subscribe_status[handle_code]:
                subscribed_list.append(handle_code)
                other_list.remove(handle_code)
    return subscribed_list, other_list
                
def get_subscribe_button_list(user_id, question_num):
    db = bot_util.connect_to_database()
    collect = db["question_table"]
    handle_code = collect.find_one({'question_num':question_num})['handle_code']
    status = get_subscribe_status(user_id,handle_code)
    
    button_list = []
    if status == "not_asked_yet":
        print("[QQQQ]:",question_num)
        collect = db["button_table"]
        B_list = collect.find_one({'question_num':question_num})['button_list']
        for item in B_list:
            button = QuickReply(item["title"], item["payload"])
            button_list.append(button)
    
    return button_list
    
def subscribe(user_id, TF, tag, space):
    #TF value is True or False correspond to subscribe or unsubscribe
    collect = connect_user_table()
    if TF:
        collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF, "subscription."+tag+"_space": space}  } )
    else:
        collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF}  } )
    
def find_user_subscribed(sub_tag):
    collect = connect_user_table()
    data = collect.find( { 'subscription.'+sub_tag : { '$exists' :True , '$in': [True] } }  )
    user_list = []
    if data is not None:
        for item in data:
            user = item["id"]
            user_list.append(user)
    
    return user_list
    
def find_user_cancel_subscribed(sub_tag):
    collect = connect_user_table()
    data = collect.find( { 'subscription.'+sub_tag+"_space" : { '$exists' :True } , 'subscription.'+sub_tag : { '$exists' :True , '$in': [False] } }  )
    user_list = []
    if data is not None:
        for item in data:
            user = item["id"]
            user_list.append(user)
    
    return user_list

def get_pushed_user(tag):
    db = connect_to_database()
    collect = db["subscription_pushed_user"]
    data = collect.find()
    if data == None:
        return []
    else:
        user_id_list = []
        for user in data:
            if user["tag"] == tag:
                user_id_list.append(user["user_id"])
        return user_id_list
        
def save_pushed_user(pushed_user_list):
    db = connect_to_database()
    collect = db["subscription_pushed_user"]
    if len(pushed_user_list) != 0:
        for user in pushed_user_list:
            R = collect.find_one({'user_id':user['user_id'],'tag':user["tag"]}) 
            if R == None:
                collect.insert(user)