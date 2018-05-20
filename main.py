from bot import bot_preprocessing
from fb_api import fb_flask

if __name__ == "__main__":
    '''
        Preprocess data for jieba dictionary that is needed for the chatbot
        The required file is put in data/ and extra_dict/ in bot/ folder respectively
        bot_config.py can be used to change the needed file location
    '''
    bot_preprocessing.init_bot_QAset()
    
    '''
        Run flask to start the FB chat service
        Code implementation exists in fb_api/ folder
    '''
    fb_flask.app.run(host='0.0.0.0', port=5000)
    
    