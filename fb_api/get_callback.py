import external_api as API
import process
import send_request as send
import mongodb as M

def get_quick_reply(user_id,payload):
	print("get quick_reply")
	
def get_text(user_id,text):
	print("{} says {}".format(user_id,text))

	mongo_client, db, collect = M.open_connection()
	if M.new_user(collect, user_id): 
		print("new user coming!")
		send.hello_to_new_user(user_id)
	
	state = M.get_state(collect, user_id)
	print("{} is in {} state".format(user_id,state))
	
	if state == "default":
		type, question_num, answer, slots = process.QA(text)
		if type == "gQA":	
			send.send_text(user_id, answer)
		elif type == "sQA":
			if slots.get("space"):	
				send.send_text(user_id, answer)
				M.save_text(collect, user_id, text)
			else:
				M.set_state(collect, user_id, "wait_location")
				send.query_location(user_id)
				M.save_text(collect, user_id, text)
		elif type == "slots":
			text = M.get_data(collect, user_id, "text")
			type, question_num, answer, slots = process.QA(text+slots['space'])
			send.send_text(user_id, answer)
		else : #neither
			send.say_something(user_id)
			print("state: neither")
		
			
	elif state == "wait_location":
		type, question_num, answer, slots = process.QA(text)
		if type == "gQA":	
			send.send_text(user_id, answer)
			M.set_state(collect, user_id, "default")
		elif type == "sQA":
			if slots.get("space"):	
				send.send_text(user_id, answer)
				M.set_state(collect, user_id, "default")
			else:
				send.query_location(user_id)
		elif type == "slots":
			if slots.get("space"):	
				text = M.get_data(collect, user_id, "text")
				type, question_num, answer, slots = process.QA(text+slots['space'])
				send.send_text(user_id, answer)
				M.set_state(collect, user_id, "default")
			else:
				send.query_location(user_id)
		else : #neither
			send.query_location(user_id)
			print("type: neither")

	M.close_connection(mongo_client)
	
def get_location(user_id,location):

	mongo_client, db, collect = M.open_connection()
	if M.new_user(collect, user_id): 
		print("new user coming!")
		send.hello_to_new_user(user_id)
	
	print (user_id,"'s location: ",location)
	area = API.get_area(location)
	print (user_id," is in ",area)
	text = "你目前在:"+area
	send.send_text(user_id, text)
	
	text = M.get_data(collect, user_id, 'text')
	print("{}'s last quesiotn is {}".format(user_id,text))
	type, question_num, answer, slots = process.QAlocation(text,area)
	send.send_text(user_id, answer)
	
	M.close_connection(mongo_client)