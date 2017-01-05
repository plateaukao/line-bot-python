from pymongo import MongoClient
import os
import re

mongodb_path = os.environ['MONGODB_URI'],

client = MongoClient(mongodb_path)

image_collection = client.heroku_0z7b2mm9.images


def addImage(userId, imageId, url, caption, messageId=None):
    record = {'userId':userId,'imageId':imageId, 'url':url,'caption':re.sub('[\s+]', '', caption), 'messageId':messageId}
    image_collection.insert_one(record)

def findImageWithCaption(userId, caption):
    return image_collection.find({'userId':userId, 'caption': re.compile(caption, re.IGNORECASE)})

def findImageWithMessageId(messageId):
    return image_collection.find({'messageId': messageId})
