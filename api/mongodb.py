import pymongo
from classes import Keywords
from pymongo import MongoClient
from settings import *

def Test():
    k = Keywords(['study'])
    ks = []
    ks.append(Keywords(['study', 'mongo', 'db', 'academia']))
    ks.append(Keywords(['study', 'db']))
    ks.append(Keywords(['academia', 'mongo', 'db']))
    # print(ks[0].similarity(ks[1]))
    # print(ks[0].similarity(ks[2]))
    # print(ks[1].similarity(ks[2]))

    client, db = open_connection()
    insert_data_keywords(db, k)
    insert_many_keywords(db, ks)
    keywords = find_many_keywords(db)
    for keyword in keywords:
        print(keyword)
    del keywords[:]
    # delete_all_keywords(db)
    # drop_collection_keywords(db)
    close_connection(client)

def open_connection():
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DBNAME]
    return client, db

def close_connection(client):
    client.close()

def insert_data_keywords(db, k):
    keywords = db.keywords
    post_id = keywords.insert_one(k.dict()).inserted_id
    return post_id

def insert_many_keywords(db, ks):
    keywords = db.keywords
    result = keywords.insert_many(k.dict() for k in ks)
    return result.inserted_ids

def find_many_keywords(db):
    result = []
    keywords = db.keywords
    for keyword in keywords.find():
        result.append(keyword)
    return result

def delete_all_keywords(db):
    keywords = db.keywords
    result = keywords.delete_many({})
    return result.deleted_count

def drop_collection_keywords(db):
    keywords = db.keywords
    keywords.drop()

if __name__ == '__main__':
    Test()