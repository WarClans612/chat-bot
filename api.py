PORT = 25555
DEBUG = False

from eve import Eve
from flask import jsonify

from api.mongodb import *
from bot import bot_function as bot


app = Eve()

@app.route('/')
def index():
    return hello_world()

@app.route('/welcome')
@app.route('/hello')
def hello_world():
    welcome = """
    Welcome to the Academia Sinica Project's REST API Server
    Please use the following route to access the features
    /qa/<question> : Asking question
    """
    print(welcome)
    return welcome

@app.route('/find')
def find_keywords():
    client, db = open_connection()
    keywords = find_many_keywords(db)
    close_connection(client)
    return str(keywords)

@app.route('/qa/<question>')
def qa_handling(question):
    # print(answers)
    # print(keyword_set)
    # answer = bot.qa_answering(question, answers, keyword_set)
    answers = 'a'
    return jsonify({'question':question, 'answer':answer})

if __name__ == '__main__':
    ### Init QA Engine
    global answers, keyword_set
    filename = 'bot/QA_examples.txt'
    questions, answers = bot.open_qa_file(filename)
    stop_words_filename = 'bot/extra_dict/stop_words.txt'
    idf_filename = 'bot/extra_dict/idf.txt.big'
    keywords, keyword_set, num_of_keyword = bot.init_jieba(stop_words_filename, idf_filename, questions)
    # print(answers)
    # print(keyword_set)

    ### Eve webserver
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)