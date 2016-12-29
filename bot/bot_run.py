#!/usr/bin/python3.4

import bot_function as bot
import method 
import sys

if len(sys.argv) < 2: #len小於2也就是不帶參數啦
	print("no argument, using [probability] for default")
	weighting_method = 'probability'
elif sys.argv[1].startswith('-'):
	option = sys.argv[1][1:] # 取出sys.argv[1]的數值但是忽略掉'--'這兩個字元
	if option == 'w': 
		weighting_method = sys.argv[2]
		print("using [",weighting_method,"] ")
	else:
		print("error: using -w for setting weighting_method ")
else:
	print("error: using -w for setting weighting_method ")
		
while 1==1:
	question = input("==>")
	words = bot.segment(question)
	scores_sorted = method.get_score(words, weighting_method)
	answer = scores_sorted[0]
	print (answer)