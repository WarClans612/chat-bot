from pymongo import MongoClient
uri = "127.0.0.1:27017" 
client = MongoClient(uri)

db = client['news']
collect = db['papers']

# create new post object

post3 = {"author": "Mike",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"]}
# insert into collection

post_id = collect.insert_one(post3).inserted_id
print (post_id) # if ObjectId('...') then successful!

for post in collect.find():
    print (post)