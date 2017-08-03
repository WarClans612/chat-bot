import pymongo
from pymongo import MongoClient
from settings import *

def open_connection():
	client = MongoClient(MONGO_HOST, MONGO_PORT)
	db = client[MONGO_DBNAME]
	collect = db[TABLE_NAME]
	return client, db, collect

def close_connection(client):
	client.close()
	
def new_user(collect, user_id):
	if collect.find_one({'id':user_id})== None:
		data = {"id": user_id,
				"state": "defult"
			}
		collect.insert_one(data)
		process.new_user(user_id)
		return True
	else:
		return False
		
def get_state(collect, user_id):
	data = collect.find_one({'id':user_id})
	state = data['state']
	return state
	
def set_state(collect, user_id, state):
	collect.find_one_and_update({'id':user_id},{'$set': {'state':state}})
	
def save_text(collect, user_id, text):
	collect.find_one_and_update({'id':user_id},{'$set': {'text':text}})
	
def get_data(collect, user_id, Column):
	data = collect.find_one({'id':user_id})[Column]
	return data

if __name__ == '__main__':
	Test()