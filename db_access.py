from pymongo import MongoClient
import os
import re

mongodb_path = os.environ['MONGODB_URI'],

client = MongoClient(mongodb_path)

image_collection = client.heroku_0z7b2mm9.images


def addImage(userId, imageId, url, caption, messageId=None, isPublic=0):
    record = {'userId':userId,'imageId':imageId, 'url':url,'caption':re.sub('[\s+]', '', caption), 'messageId':messageId, 'isPublic':isPublic}
    image_collection.insert_one(record)

def findImageWithCaption(userId, caption):
    items = image_collection.find({'userId':userId, 'caption': re.compile(caption, re.IGNORECASE)})
    public_items = image_collection.find({'userId':{'$ne': userId}, 'caption': re.compile(caption, re.IGNORECASE), 'isPublic':1})
    return items.extend(public_items)

def findImageWithMessageId(messageId):
    return image_collection.find({'messageId': messageId})
