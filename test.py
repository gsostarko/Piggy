from pymongo import MongoClient

from bson.objectid import ObjectId

client = MongoClient("mongodb://mongo:wvVg7SpdTrlt4RC1Z844@containers-us-west-117.railway.app:6622")

db = client.kolinje
entries = []
filter = {}


podaci = db.recepture.find(filter)
recepti_temp = []
for each_doc in podaci:
    recepti_temp.append(each_doc)

print(recepti_temp)

print(db.recepti.find({"_id": "6377c6baab10fb0e9b22b691"}))

vaganje_id = ObjectId()

print(vaganje_id)