#!/usr/bin/python3.4

import bot_function as bot
import bot_config
import method 
import sys

#frequency ratio probability weight_e

filename = bot_config.QAset

weighting_method = 'probability'
output_file = 'output_{}.txt'.format(weighting_method)

fail_count = 0
success_count = 0

question_set, answer_set = bot.open_qa_file(filename)
with open(output_file, 'w', encoding='utf8') as fw:		
	fw.write('input filename'+filename+'\n')
	fw.write('output: question failed\n\n')
	for i in range(len(question_set)):
		question = question_set[i]
		words = bot.segment(question)
		scores_sorted = method.get_score(words, weighting_method)
		answer = scores_sorted[0][0]
		score = str(scores_sorted[0][1])
		if answer != answer_set[i]:
			fail_count = fail_count+1
			fw.write('Q          : '+question_set[i]+'\n')
			fw.write('A_correct  : '+answer_set[i]+'\n')
			fw.write('A_answering: '+answer+'\n')
			fw.write('words_of_Q : '+' '.join(words)+'\n')
			fw.write('score      : '+score+'\n\n')
		elif  answer == answer_set[i]:
			success_count = success_count+1
		else:
			print('error')
print('fail_count : ',fail_count)
print('success_count : ',success_count)