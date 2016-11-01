my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
}

from eve import Eve
app = Eve(settings=my_settings)
PORT = 25555
DEBUG = False

if __name__ == '__main__':
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)