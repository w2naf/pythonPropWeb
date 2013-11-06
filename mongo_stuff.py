import pymongo
from bson.objectid import ObjectId

mongo         = pymongo.MongoClient()
entries_coll  = mongo.voacap.entries
