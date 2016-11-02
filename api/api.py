my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
}

PORT = 25555
DEBUG = False

from eve import Eve
app = Eve(settings=my_settings)

if __name__ == '__main__':
    app.run(port=PORT, host='0.0.0.0', debug=DEBUG)