from fb_api import external_api
from fb_api import process
from fb_api import send_request
from fb_api import mongodb
import re

def get_quick_reply(user_id,payload):
    mongo_client, db, collect = mongodb.open_connection()
    
    fun_pattern = "_FUN=(([A-Z])\w+)_"
    tag_pattern = "_TAG=(([A-Z])\w+)_"
    loc_pattern = "_LOC=(([\u4e00-\u9fa5])+)_"
    fun_match = re.search(fun_pattern,payload)
    tag_match = re.search(tag_pattern,payload)
    loc_match = re.search(loc_pattern,payload)
    if fun_match !=  None: 
        FUN = fun_match.group(1)
        tag = tag_match.group(1)
        print ("FUNNNNNN="+FUN)
        if FUN == "SUB":
            space = mongodb.check_space(collect, user_id)
            if space == None:
                send_request.query_subscription_location(user_id)
                mongodb.save_tag_want_to_subscribe(collect, user_id, tag)
                mongodb.set_state(collect, user_id, "wait_subscription_location")
            else:
                send_request.send_subscribe_ask(user_id,tag,space)
        elif FUN == "NEVERSUB" or FUN == "UNSUB":
            TF = False
            mongodb.subscribe(collect, user_id, TF, tag, "")
            send_request.send_subscribe_mess(user_id, TF, tag, "")
        elif FUN == "SUBYES" :
            TF = True
            space = loc_match.group(1)
            mongodb.subscribe(collect, user_id, TF, tag, space)
            send_request.send_subscribe_mess(user_id, TF, tag, space)
        elif FUN == "SUBOTHER" :
            send_request.query_subscription_location(user_id)
            mongodb.save_tag_want_to_subscribe(collect, user_id, tag)
            mongodb.set_state(collect, user_id, "wait_subscription_location")
        else:
            print("[ERR] no such FUN payload")
            
    elif payload == "SET_DEFAULT":
        mongodb.set_state(collect, user_id, "default")
        send_request.send_cancel(user_id)
        
    print("get quick_reply: ", payload)
    
    mongodb.close_connection(mongo_client)
    
def get_text(user_id,text):
    mongo_client, db, collect = mongodb.open_connection()
    if mongodb.new_user(db, user_id): 
        print("new user coming!")
        send_request.hello_to_new_user(user_id)
    
    state = mongodb.get_state(collect, user_id)
    print("{} is in {} state".format(user_id,state))
    
    if state == "default":
        type, question_num, slots = process.QA(text)
        print("[slots]",slots)
        
        if slots.get("time"):
            mongodb.save_time(collect, user_id, slots["time"])
        else:
            time = mongodb.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
            
        print("{}'s type is {}".format(user_id,type))
        if type == "iQA":
            answer = process.iQA_get_answer(question_num,slots)
            send_request.send_text(user_id, answer)
        elif type == "gQA": 
            answer = process.gQA_get_answer(question_num)
            send_request.send_text(user_id, answer)
        elif type == "sQA_with_space":
            mongodb.save_space(collect, user_id, slots["space"])
            answer = process.sQA_get_answer(question_num,slots)
            button_list = mongodb.get_subscribe_button_list(db,user_id,question_num)
            send_request.send_sQA_answer(user_id,answer,button_list)
            mongodb.save_qnum(collect, user_id, question_num)
        elif type == "sQA_without_space":
            space = mongodb.check_space(collect, user_id) 
            if space == None:
                mongodb.set_state(collect, user_id, "wait_location")
                send_request.query_location(user_id)
                mongodb.save_qnum(collect, user_id, question_num)
            else:
                slots["space"] = space
                answer = process.sQA_get_answer(question_num,slots)
                button_list = mongodb.get_subscribe_button_list(db,user_id,question_num)
                send_request.send_sQA_answer(user_id,answer,button_list)
                mongodb.save_qnum(collect, user_id, question_num)
        elif type == "space_and_time" or type == "space" :
            mongodb.save_space(collect, user_id, slots["space"])
            last_q_num = mongodb.get_data(collect, user_id, "question_num")
            answer = process.sQA_get_answer(last_q_num,slots)
            button_list = mongodb.get_subscribe_button_list(db,user_id,last_q_num)
            send_request.send_sQA_answer(user_id,answer,button_list)
        elif type == "time":
            space = mongodb.check_space(collect, user_id) 
            if space != None:
                slots["space"] = space
                last_q_num = mongodb.get_data(collect, user_id, "question_num")
                answer = process.sQA_get_answer(last_q_num,slots)
                button_list = mongodb.get_subscribe_button_list(db,user_id,last_q_num)
                send_request.send_sQA_answer(user_id,answer,button_list)
            else:
                send_request.say_something(user_id)
        elif type == "SUB":
            subscribed_list, other_list = mongodb.get_all_subscribe_status(collect,user_id)
            send_request.send_sublist(user_id, other_list)
        elif type == "UNSUB":
            subscribed_list, other_list = mongodb.get_all_subscribe_status(collect,user_id)
            send_request.send_unsublist(user_id, subscribed_list)
        else : #neither
            send_request.say_something(user_id)
            print("state: neither")
        
            
    elif state == "wait_location":
        type, question_num, slots = process.QA(text)
        
        if slots.get("time"):
            mongodb.save_time(collect, user_id, slots["time"])
        else:
            time = mongodb.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
        
        print("{}'s type is {}".format(user_id,type))
        if type == "gQA":   
            answer = process.gQA_get_answer(question_num)
            send_request.send_text(user_id, answer)
            mongodb.set_state(collect, user_id, "default")
        elif type == "sQA_with_space":
            mongodb.save_space(collect, user_id, slots["space"])
            answer = process.sQA_get_answer(question_num,slots)
            button_list = mongodb.get_subscribe_button_list(db,user_id,question_num)
            send_request.send_sQA_answer(user_id,answer,button_list)
            mongodb.set_state(collect, user_id, "default")
            mongodb.save_qnum(collect, user_id, question_num)
        elif type == "sQA_without_space":
            send_request.query_location(user_id)
            mongodb.save_qnum(collect, user_id, question_num)
        elif type == "space_and_time" or type == "space":
            mongodb.save_space(collect, user_id, slots["space"])
            last_q_num = mongodb.get_data(collect, user_id, "question_num")
            answer = process.sQA_get_answer(last_q_num,slots)
            button_list = mongodb.get_subscribe_button_list(db,user_id,last_q_num)
            send_request.send_sQA_answer(user_id,answer,button_list)
            mongodb.set_state(collect, user_id, "default")
        else : # time or neither
            send_request.query_location(user_id)
            print("type: neither")
            
    elif state == "wait_subscription_location":
        type, question_num, slots = process.QA(text)
        
        if slots.get("time"):
            mongodb.save_time(collect, user_id, slots["time"])
        else:
            time = mongodb.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
        
        if slots.get("space"):
            mongodb.save_space(collect, user_id, slots["space"])
            TF = True
            space = slots["space"]
            tag = mongodb.get_data(collect, user_id, "tag_want")
            mongodb.subscribe(collect, user_id, TF, tag, space)
            send_request.send_subscribe_mess(user_id, TF, tag, space)
            mongodb.set_state(collect, user_id, "default")
        else : 
            send_request.query_subscription_location(user_id)

    mongodb.close_connection(mongo_client)
    
def get_location(user_id,location):

    mongo_client, db, collect = mongodb.open_connection()
    if mongodb.new_user(db, user_id): 
        print("new user coming!")
        send_request.hello_to_new_user(user_id)
        

    print (user_id,"'s location: ",location)
    country,area = external_api.get_area(location)
    print (user_id," is in ",area)
    text = "你目前在:"+country+area
    send_request.send_text(user_id, text)
    slots = {}
    slots["space"] = country
    
    mongodb.save_space(collect, user_id, slots["space"])
    
    state = mongodb.get_state(collect, user_id)
    if state == "wait_subscription_location":
        TF = True
        space = slots["space"]
        tag = mongodb.get_data(collect, user_id, "tag_want")
        mongodb.subscribe(collect, user_id, TF, tag, space)
        send_request.send_subscribe_mess(user_id, TF, tag, space)
        mongodb.set_state(collect, user_id, "default")
            
    else:
        last_q_num = mongodb.get_data(collect, user_id, "question_num")
        print("{}'s last quesiotn is {}".format(user_id,last_q_num))
        answer = process.sQA_location_get_answer(last_q_num,slots,location)
        button_list = mongodb.get_subscribe_button_list(db,user_id,last_q_num)
        send_request.send_sQA_answer(user_id,answer,button_list)
        mongodb.set_state(collect, user_id, "default")
    
    mongodb.close_connection(mongo_client)
