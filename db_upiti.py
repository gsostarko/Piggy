import pymongo
import datetime 

#client = pymongo.MongoClient("mongodb+srv://gsostarko:mmsw.32E@cluster0.adehxey.mongodb.net/?retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb://mongo:wvVg7SpdTrlt4RC1Z844@containers-us-west-117.railway.app:6622")

db = client['kolinje']

#collections
recepture = db['recepture']
korisnici = db['korisnici']
termin_kolinja = db['termin_kolinja']

db = client.get_database('kolinje')
collection = db.get_collection('recepture')



filter = {'Naslov_recepta': 'test'}

podaci = collection.find(filter)
print(podaci)

recepti_temp = []
for each_doc in podaci:
    recepti_temp.append(each_doc)
    print(each_doc['Naslov_recepta'])

print(recepti_temp[0])