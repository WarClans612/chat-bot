PORT = 25555
DEBUG = False

from flask import Flask
from mongodb import *
app = Flask(__name__)

@app.route('/hello')
def hello_world():
    welcome = """
    Welcome to the Academia Sinica Project's REST API Server
    Please use the following route to access the features
    /find : find keywords
    """
    return welcome

@app.route('/find')
def find_keywords():
    client, db = open_connection()
    keywords = find_many_keywords(db)
    close_connection(client)
    return str(keywords)

if __name__ == '__main__':
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)
