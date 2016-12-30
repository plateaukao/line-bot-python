from pymongo import MongoClient
import os

mongodb_path = os.environ['MONGODB_URI'],

client = MongoClient(mongodb_path)

image_collection = client.heroku_0z7b2mm9.images


def addImage(userId, imageId, url, caption):
    record = {'userId':userId,'imageId':imageId, 'url':url,'caption':caption}
    image_collection.insert_one(record)
