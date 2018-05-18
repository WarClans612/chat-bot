import pymongo
from pymongo import MongoClient
from fb_api.fb_config import *
from fb_api.pymessager.message import QuickReply
import datetime as DT
from datetime import datetime
handle_list = ["WEATHER","RAIN","PM25","GOOUT","UVI"]

def open_connection():
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DBNAME]
    collect = db[TABLE_NAME]
    return client, db, collect

def close_connection(client):
    client.close()
    
def new_user(db, user_id):
    collect = db["question_table"]
    init_question = collect.find_one({"handle_code":"WEATHER"})["question_num"]
    
    collect = db[TABLE_NAME]
    if collect.find_one({'id':user_id})== None:
        data = {"id": user_id,
                "state": "default",
                "question_num": init_question,
                "subscription" : {}
            }
        collect.insert_one(data)
        return True
    else:
        return False
        
def get_state(collect, user_id):
    data = collect.find_one({'id':user_id})
    state = data['state']
    return state
    
def set_state(collect, user_id, state):
    collect.find_one_and_update({'id':user_id},{'$set': {'state':state}})

def save_qnum(collect, user_id, question_num):
    collect.find_one_and_update({'id':user_id},{'$set': {'question_num':question_num}})
    
def save_tag_want_to_subscribe(collect, user_id, tag_want):
    collect.find_one_and_update({'id':user_id},{'$set': {'tag_want':tag_want}})
    
def save_space(collect, user_id, space):
    now_time = datetime.now()
    collect.find_one_and_update({'id':user_id},{'$set': {'space':space, 'space_time':now_time }})

def save_time(collect, user_id, time):
    now_time = datetime.now()
    collect.find_one_and_update({'id':user_id},{'$set': {'time':time, 'time_time':now_time }})
    
def check_space(collect, user_id):
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
        
def check_time(collect, user_id):
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
    
    
def get_data(collect, user_id, Column):
    data = collect.find_one({'id':user_id})[Column]
    return data
    
def get_subscribe_status(collect,user_id,handle_code):
    subscribe_status = collect.find_one({'id':user_id})['subscription']
    if subscribe_status.get(handle_code):
        if subscribe_status[handle_code] == True:
            return "subscribed"
        else:
            return "never_asked"
    else:
        return "not_asked_yet"
        
def get_subscribe_space(collect,user_id,handle_code):
    item = collect.find_one({'id':user_id})
    print(item)
    subscribe_status = item['subscription']
    if subscribe_status.get(handle_code):
        space = subscribe_status[handle_code+"_space"]
        return space
    else:
        return None
        
def get_all_subscribe_status(collect,user_id):
    subscribe_status = collect.find_one({'id':user_id})['subscription']
    subscribed_list = []
    other_list = handle_list.copy()
    for handle_code in handle_list:
        if subscribe_status.get(handle_code):
            if subscribe_status[handle_code] == True:
                subscribed_list.append(handle_code)
                other_list.remove(handle_code)
    return subscribed_list, other_list
                
        
def get_subscribe_button_list(db,user_id,question_num):
    handle_code = db.question_table.find_one({'question_num':question_num})['handle_code']
    status = get_subscribe_status(db[TABLE_NAME],user_id,handle_code)
    
    button_list = []
    if status == "not_asked_yet":
        print("[QQQQ]:",question_num)
        B_list = db.button_table.find_one({'question_num':question_num})['button_list']
        for item in B_list:
            button = QuickReply(item["title"], item["payload"])
            button_list.append(button)
    
    return button_list
    
def subscribe(collect, user_id, TF, tag, space):
    if TF == True:
        collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF, "subscription."+tag+"_space": space}  } )
    else:
        collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF}  } )
    
def find_user_subscribed(collect, sub_tag):
    data = collect.find( { 'subscription.'+sub_tag : { '$exists' :True , '$in': [True] } }  )
    user_list = []
    if data != None:
        for item in data:
            user = item["id"]
            user_list.append(user)
    
    return user_list
    
def find_user_cancel_subscribed(collect, sub_tag):
    data = collect.find( { 'subscription.'+sub_tag+"_space" : { '$exists' :True } , 'subscription.'+sub_tag : { '$exists' :True , '$in': [False] } }  )
    user_list = []
    if data != None:
        for item in data:
            user = item["id"]
            user_list.append(user)
    
    return user_list

def get_pushed_user(db, tag):
    data = db.subscription_pushed_user.find()
    if data == None:
        return []
    else:
        user_id_list = []
        for user in data:
            if user["tag"] == tag:
                user_id_list.append(user["user_id"])
        return user_id_list
        
def save_pushed_user(db, pushed_user_list):
    if len(pushed_user_list) != 0:
        for user in pushed_user_list:
            R = db.subscription_pushed_user.find_one({'user_id':user['user_id'],'tag':user["tag"]}) 
            if R == None:
                db.subscription_pushed_user.insert(user) 

if __name__ == '__main__':
    client,db,collect = open_connection()
    new_user(db, user_id)       
    close_connection(client)
