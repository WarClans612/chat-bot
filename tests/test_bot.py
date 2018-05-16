# -*- coding: utf-8 -*-

import sys
import os
PWD = os.getcwd()
sys.path.append(PWD)

import unittest

class BotTest(unittest.TestCase):
    ###############################################################
    #Test for bot/bot_preprocessing.py
    def test_init_bot_QAset(self):
        from bot.bot_preprocessing import init_bot_QAset
        
        #test init bot QAset
        self.assertTrue(init_bot_QAset())
        
    ###############################################################
    #Test for bot/method.py
    def test_get_score(self):
        from bot.method import get_score
        
        question = ["今天","天氣", "老人家"]
        self.assertIsNotNone(get_score(question, 'frequency'))
        self.assertIsNotNone(get_score(question, 'ratio'))
        self.assertIsNotNone(get_score(question, 'probability'))
        self.assertIsNotNone(get_score(question, 'weight_e'))
        self.assertIsNotNone(get_score(question, 'fre_prob'))
        self.assertIsNotNone(get_score(question, 'combination'))
        
    #Test for bot/method.py
    def test_integrateQA(self):
        from bot.method import integrateQA
        
        question = ["今天","天氣"]
        self.assertIsNotNone(integrateQA(question))
        
    ###############################################################
    #Test for bot/bot_function.py
    def test_segment(self):
        from bot.bot_function import segment
        
        #Check if the result is empty list or not
        self.assertFalse(segment(""))
        self.assertTrue(segment("今天天氣"))
        self.assertTrue(segment("為什麼老人容易受到PM2.5的影響?"))
        self.assertTrue(segment("如何判斷自己已得了糖尿病或糖尿病正在自己體内進行中?"))
        self.assertTrue(segment("什麼是UVI?"))
        
    def test_get_answer(self):
        from bot.bot_function import get_answer, default_message
        
        #Initialize slots
        slots = {}
        slots['space'] = "基隆"
        slots['time'] = "now"
        
        #Test first 226 question num
        for question_num in range(226):
            self.assertNotEqual(get_answer(question_num+1, slots), default_message)
            
    def test_get_slots(self):
        from bot.bot_function import get_slots
        
        slots_key = ['space', 'time']
        words = ['今天' ,'臺南', '溫度']
        slots, rest_words = get_slots(words)
        #Testing if key is in slots return
        for keys in slots_key:
            self.assertIn(keys, slots) 

    ###############################################################
    
if __name__ == "__main__":
    unittest.main()