import os
from pymongo import MongoClient
from prettyprinter import pprint
from bson.objectid import ObjectId


client = MongoClient(os.environ.get("MONGODB_URI"))
db = client.kolinje

class Upiti():
    def filtriranje_vaganja():
        popis = list(db.kolinja.find({"_id": ObjectId("637e65495581cd2e56d0b050")},{"vaganja.tezina_mesa":1}))
        #pprint(list(popis))

        id_kolinja = []
        output=[]
        for i in db.kolinja.find({},{"_id": 1}):
            id_kolinja.append(i)
        for j in id_kolinja:
            print(j)
            lista = list(db.kolinja.find({"_id":j['_id']},{"vaganja.tezina_mesa":1}))
            print(lista)
            output.append(lista)
        # for i in id_kolinja:
        #     dict = list(db.kolinja.find({"_id": id_kolinja[i]}))
        
        
        return output