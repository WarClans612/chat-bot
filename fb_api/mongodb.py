import pymongo
from pymongo import MongoClient
import datetime as DT
from datetime import datetime
from bot.util import BotUtil
from fb_api.fb_config import *
from fb_api.pymessager.message import QuickReply
handle_list = ["WEATHER","RAIN","PM25","GOOUT","UVI"]

#Connect to USER_INFO database
def _connect_to_database():
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DBNAME]
    return db
    
#Return collect directly for the USER_INFO table
def _connect_user_table():
    db = _connect_to_database()
    return db[USER_INFO]

class MongoDB:
    _fb_db = _connect_to_database()
    _fb_user_collect = _connect_user_table()
    _bot_client = BotUtil()
    _bot_db = _bot_client._bot_db
    
    #Check if the user_id exist in the database
    def new_user(self, user_id):
        collect = self._bot_db["question_table"]
        init_question = collect.find_one({"handle_code":"WEATHER"})["question_num"]
        
        if self._fb_user_collect.find_one({'id':user_id}) is None:
            data = {"id": user_id,
                    "state": "default",
                    "question_num": init_question,
                    "subscription" : {}
                }
            collect.insert_one(data)
            return True
        else:
            return False
    
    def get_state(self, user_id):
        data = self._fb_user_collect.find_one({'id':user_id})
        state = data['state']
        return state
        
    def set_state(self, user_id, state):
        self._fb_user_collect.find_one_and_update({'id':user_id},{'$set': {'state':state}})
    
    def save_qnum(self, user_id, question_num):
        self._fb_user_collect.find_one_and_update({'id':user_id},{'$set': {'question_num':question_num}})
        
    def save_tag_want_to_subscribe(self, user_id, tag_want):
        self._fb_user_collect.find_one_and_update({'id':user_id},{'$set': {'tag_want':tag_want}})
        
    def save_space(self, user_id, space):
        now_time = datetime.now()
        self._fb_user_collect.find_one_and_update({'id':user_id},{'$set': {'space':space, 'space_time':now_time }})
    
    def save_time(self, user_id, time):
        now_time = datetime.now()
        self._fb_user_collect.find_one_and_update({'id':user_id},{'$set': {'time':time, 'time_time':now_time }})
        
    def check_space(self, user_id):
        data = self._fb_user_collect.find_one({'id':user_id})
        if data.get("space"):
            now_time = datetime.now()
            ten_mins = DT.timedelta( days=30 )
            if now_time - data["space_time"] < ten_mins:
                return data["space"]
            else:
                return None
        else:
            return None
            
    def check_time(self, user_id):
        data = self._fb_user_collect.find_one({'id':user_id})
        if data.get("time"):
            now_time = datetime.now()
            three_mins = DT.timedelta( minutes=3 )
            if now_time - data["time_time"] < three_mins:
                return data["time"]
            else:
                return None
        else:
            return None
    
    def get_data(self, user_id, Column):
        data = self._fb_user_collect.find_one({'id':user_id})[Column]
        return data
        
    def get_subscribe_status(self, user_id, handle_code):
        subscribe_status = self._fb_user_collect.find_one({'id':user_id})['subscription']
        if subscribe_status.get(handle_code):
            if subscribe_status[handle_code]:
                return "subscribed"
            else:
                return "never_asked"
        else:
            return "not_asked_yet"
            
    def get_subscribe_space(self, user_id, handle_code):
        item = self._fb_user_collect.find_one({'id':user_id})
        subscribe_status = item['subscription']
        if subscribe_status.get(handle_code):
            space = subscribe_status[handle_code+"_space"]
            return space
        else:
            return None
            
    def get_all_subscribe_status(self, user_id):
        subscribe_status = self._fb_user_collect.find_one({'id':user_id})['subscription']
        subscribed_list = []
        other_list = handle_list.copy()
        for handle_code in handle_list:
            if subscribe_status.get(handle_code):
                if subscribe_status[handle_code]:
                    subscribed_list.append(handle_code)
                    other_list.remove(handle_code)
        return subscribed_list, other_list
                    
    def get_subscribe_button_list(self, user_id, question_num):
        collect = self._bot_db["question_table"]
        handle_code = collect.find_one({'question_num':question_num})['handle_code']
        status = self.get_subscribe_status(user_id,handle_code)
        
        button_list = []
        if status == "not_asked_yet":
            print("[QQQQ]:",question_num)
            collect = self._bot_db["button_table"]
            B_list = collect.find_one({'question_num':question_num})['button_list']
            for item in B_list:
                button = QuickReply(item["title"], item["payload"])
                button_list.append(button)
        
        return button_list
        
    def subscribe(self, user_id, TF, tag, space):
        #TF value is True or False correspond to subscribe or unsubscribe
        if TF:
            self._fb_user_collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF, "subscription."+tag+"_space": space}  } )
        else:
            self._fb_user_collect.find_one_and_update( {'id':user_id}, { '$set' : { "subscription."+tag: TF}  } )
        
    def find_user_subscribed(self, sub_tag):
        data = self._fb_user_collect.find( { 'subscription.'+sub_tag : { '$exists' :True , '$in': [True] } }  )
        user_list = []
        if data is not None:
            for item in data:
                user = item["id"]
                user_list.append(user)
        
        return user_list
        
    def find_user_cancel_subscribed(self, sub_tag):
        data = self._fb_user_collect.find( { 'subscription.'+sub_tag+"_space" : { '$exists' :True } , 'subscription.'+sub_tag : { '$exists' :True , '$in': [False] } }  )
        user_list = []
        if data is not None:
            for item in data:
                user = item["id"]
                user_list.append(user)
        
        return user_list
    
    def get_pushed_user(self, tag):
        collect = self._bot_db["subscription_pushed_user"]
        data = collect.find()
        if data is None:
            return []
        else:
            user_id_list = []
            for user in data:
                if user["tag"] == tag:
                    user_id_list.append(user["user_id"])
            return user_id_list
            
    def save_pushed_user(self, pushed_user_list):
        collect = self._bot_db["subscription_pushed_user"]
        if len(pushed_user_list) != 0:
            for user in pushed_user_list:
                R = collect.find_one({'user_id':user['user_id'],'tag':user["tag"]}) 
                if R is None:
                    collect.insert(user)