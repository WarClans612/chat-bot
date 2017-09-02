import sys
sys.path.append("C:/Users/plum/Documents/Python Scripts/chat-bot")
from bot import bot_config
from bot import bot_function as bot
from bot import method 
import re

from pymessager.message import Messager
from pymessager.message import QuickReply
from pymessager.message import ContentType

from fb_api_config import facebook_access_token 
from fb_api_config import verification_code

def QA(question):
	words = bot.segment(question)
	slots, rest_words = bot.get_slots(words)
	if len(rest_words) == 0:
		type = "neither"
		question_num = 0
	elif "訂閱" in rest_words:
		if "取消" in rest_words:
			type = "UNSUB"
			question_num = 0
		else:
			type = "SUB"
			question_num = 0
	else:
		type, question_num = method.integrateQA(rest_words)
		
	if type == "iQA":
		type = "iQA"
	elif type == "gQA":
		type = "gQA"
	elif type == "sQA":
		if slots.get("space"):
			type = "sQA_with_space"
		else:	
			type = "sQA_without_space"
	elif type == "SUB":
		type = "SUB"
	elif type == "UNSUB":
		type = "UNSUB"
	else: 
		if slots.get('space') and slots.get('time'):
			type = "space_and_time"
		elif slots.get('space'):
			type = "space"
		elif slots.get('time'):
			type = "time"
		else:
			type = "neither"
	return type, question_num, slots

def gQA_get_answer(question_num):
	answer = bot.get_answer(question_num,{})
	return answer
	
def sQA_get_answer(question_num,slots):
	answer = bot.get_answer(question_num,slots.copy())
	return answer
	
def iQA_get_answer(question_num,slots): 
	answer = bot.get_answer(question_num,slots)
	return answer
	
def sQA_location_get_answer(question_num,slots,location):
	answer = bot.get_location_sQA_answer(question_num,slots.copy(),location)
	return answer
	
	
def QAlocation(question,location):
	words = bot.segment(question+location)
	slots, rest_words = bot.get_slots(words)
	type, question_num = method.integrateQA(rest_words)
	if type == "sQA" :
		answer = bot.get_answer(question_num,slots)
	else: 
		answer = ""
		print ("Err: not correct type (sQA)")
	return type, question_num, answer, slots
	
def old_QAlocation(question,location):
	weighting_method = 'fre_prob'
	words = bot.segment(question)
	words2 = bot.segment(location)
	words.extend(words2)
	scores_sorted = method.get_score(words, weighting_method)
	slots, rest_words = bot.get_slots(words)
	question_num = scores_sorted[0][0]
	answer = bot.get_answer(question_num,slots)
	return answer

	
	
def old_QA(question):
	weighting_method = 'fre_prob'
	words = bot.segment(question)
	#print(words)
	scores_sorted = method.get_score(words, weighting_method)
	slots, rest_words = bot.get_slots(words)
	print(slots)
	if "space" not in slots:
		return 1,""
	question_num = scores_sorted[0][0]
	answer = bot.get_answer(question_num,slots)
	#print (answer)
	
	return 0,answer