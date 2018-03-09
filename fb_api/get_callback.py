import external_api as API
import process
import send_request as send
import mongodb as M
import re


def get_quick_reply(user_id,payload):
    mongo_client, db, collect = M.open_connection()
    
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
            space = M.check_space(collect, user_id)
            if space == None:
                send.query_subscription_location(user_id)
                M.save_tag_want_to_subscribe(collect, user_id, tag)
                M.set_state(collect, user_id, "wait_subscription_location")
            else:
                send.send_subscribe_ask(user_id,tag,space)
        elif FUN == "NEVERSUB" or FUN == "UNSUB":
            TF = False
            M.subscribe(collect, user_id, TF, tag, "")
            send.send_subscribe_mess(user_id, TF, tag, "")
        elif FUN == "SUBYES" :
            TF = True
            space = loc_match.group(1)
            M.subscribe(collect, user_id, TF, tag, space)
            send.send_subscribe_mess(user_id, TF, tag, space)
        elif FUN == "SUBOTHER" :
            send.query_subscription_location(user_id)
            M.save_tag_want_to_subscribe(collect, user_id, tag)
            M.set_state(collect, user_id, "wait_subscription_location")
        else:
            print("[ERR] no such FUN payload")
            
    elif payload == "SET_DEFAULT":
        M.set_state(collect, user_id, "default")
        send.send_cancel(user_id)
        
    print("get quick_reply: ", payload)
    
    M.close_connection(mongo_client)
    
def get_text(user_id,text):
    mongo_client, db, collect = M.open_connection()
    if M.new_user(db, user_id): 
        print("new user coming!")
        send.hello_to_new_user(user_id)
    
    state = M.get_state(collect, user_id)
    print("{} is in {} state".format(user_id,state))
    
    if state == "default":
        type, question_num, slots = process.QA(text)
        print("[slots]",slots)
        
        if slots.get("time"):
            M.save_time(collect, user_id, slots["time"])
        else:
            time = M.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
            
        print("{}'s type is {}".format(user_id,type))
        if type == "iQA":
            answer = process.iQA_get_answer(question_num,slots)
            send.send_text(user_id, answer)
        elif type == "gQA": 
            answer = process.gQA_get_answer(question_num)
            send.send_text(user_id, answer)
        elif type == "sQA_with_space":
            M.save_space(collect, user_id, slots["space"])
            answer = process.sQA_get_answer(question_num,slots)
            button_list = M.get_subscribe_button_list(db,user_id,question_num)
            send.send_sQA_answer(user_id,answer,button_list)
            M.save_qnum(collect, user_id, question_num)
        elif type == "sQA_without_space":
            space = M.check_space(collect, user_id) 
            if space == None:
                M.set_state(collect, user_id, "wait_location")
                send.query_location(user_id)
                M.save_qnum(collect, user_id, question_num)
            else:
                slots["space"] = space
                answer = process.sQA_get_answer(question_num,slots)
                button_list = M.get_subscribe_button_list(db,user_id,question_num)
                send.send_sQA_answer(user_id,answer,button_list)
                M.save_qnum(collect, user_id, question_num)
        elif type == "space_and_time" or type == "space" :
            M.save_space(collect, user_id, slots["space"])
            last_q_num = M.get_data(collect, user_id, "question_num")
            answer = process.sQA_get_answer(last_q_num,slots)
            button_list = M.get_subscribe_button_list(db,user_id,last_q_num)
            send.send_sQA_answer(user_id,answer,button_list)
        elif type == "time":
            space = M.check_space(collect, user_id) 
            if space != None:
                slots["space"] = space
                last_q_num = M.get_data(collect, user_id, "question_num")
                answer = process.sQA_get_answer(last_q_num,slots)
                button_list = M.get_subscribe_button_list(db,user_id,last_q_num)
                send.send_sQA_answer(user_id,answer,button_list)
            else:
                send.say_something(user_id)
        elif type == "SUB":
            subscribed_list, other_list = M.get_all_subscribe_status(collect,user_id)
            send.send_sublist(user_id, other_list)
        elif type == "UNSUB":
            subscribed_list, other_list = M.get_all_subscribe_status(collect,user_id)
            send.send_unsublist(user_id, subscribed_list)
        else : #neither
            send.say_something(user_id)
            print("state: neither")
        
            
    elif state == "wait_location":
        type, question_num, slots = process.QA(text)
        
        if slots.get("time"):
            M.save_time(collect, user_id, slots["time"])
        else:
            time = M.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
        
        print("{}'s type is {}".format(user_id,type))
        if type == "gQA":   
            answer = process.gQA_get_answer(question_num)
            send.send_text(user_id, answer)
            M.set_state(collect, user_id, "default")
        elif type == "sQA_with_space":
            M.save_space(collect, user_id, slots["space"])
            answer = process.sQA_get_answer(question_num,slots)
            button_list = M.get_subscribe_button_list(db,user_id,question_num)
            send.send_sQA_answer(user_id,answer,button_list)
            M.set_state(collect, user_id, "default")
            M.save_qnum(collect, user_id, question_num)
        elif type == "sQA_without_space":
            send.query_location(user_id)
            M.save_qnum(collect, user_id, question_num)
        elif type == "space_and_time" or type == "space":
            M.save_space(collect, user_id, slots["space"])
            last_q_num = M.get_data(collect, user_id, "question_num")
            answer = process.sQA_get_answer(last_q_num,slots)
            button_list = M.get_subscribe_button_list(db,user_id,last_q_num)
            send.send_sQA_answer(user_id,answer,button_list)
            M.set_state(collect, user_id, "default")
        else : # time or neither
            send.query_location(user_id)
            print("type: neither")
            
    elif state == "wait_subscription_location":
        type, question_num, slots = process.QA(text)
        
        if slots.get("time"):
            M.save_time(collect, user_id, slots["time"])
        else:
            time = M.check_time(collect, user_id)
            if time != None:
                slots["time"] = time
        
        if slots.get("space"):
            M.save_space(collect, user_id, slots["space"])
            TF = True
            space = slots["space"]
            tag = M.get_data(collect, user_id, "tag_want")
            M.subscribe(collect, user_id, TF, tag, space)
            send.send_subscribe_mess(user_id, TF, tag, space)
            M.set_state(collect, user_id, "default")
        else : 
            send.query_subscription_location(user_id)

    M.close_connection(mongo_client)
    
def get_location(user_id,location):

    mongo_client, db, collect = M.open_connection()
    if M.new_user(db, user_id): 
        print("new user coming!")
        send.hello_to_new_user(user_id)
        

    print (user_id,"'s location: ",location)
    country,area = API.get_area(location)
    print (user_id," is in ",area)
    text = "你目前在:"+country+area
    send.send_text(user_id, text)
    slots = {}
    slots["space"] = country
    
    M.save_space(collect, user_id, slots["space"])
    
    state = M.get_state(collect, user_id)
    if state == "wait_subscription_location":
        TF = True
        space = slots["space"]
        tag = M.get_data(collect, user_id, "tag_want")
        M.subscribe(collect, user_id, TF, tag, space)
        send.send_subscribe_mess(user_id, TF, tag, space)
        M.set_state(collect, user_id, "default")
            
    else:
        last_q_num = M.get_data(collect, user_id, "question_num")
        print("{}'s last quesiotn is {}".format(user_id,last_q_num))
        answer = process.sQA_location_get_answer(last_q_num,slots,location)
        button_list = M.get_subscribe_button_list(db,user_id,last_q_num)
        send.send_sQA_answer(user_id,answer,button_list)
        M.set_state(collect, user_id, "default")
    
    M.close_connection(mongo_client)
