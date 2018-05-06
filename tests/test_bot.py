# -*- coding: utf-8 -*-

import sys
import os
PWD = os.getcwd()
sys.path.append(PWD)

import unittest

class BotTest(unittest.TestCase):
    #Test for bot/bot_preprocessing.py
    def test_init_bot_QAset(self):
        from bot.bot_preprocessing import init_bot_QAset
        
        #test init bot QAset
        self.assertTrue(init_bot_QAset())

if __name__ == "__main__":
    unittest.main()
