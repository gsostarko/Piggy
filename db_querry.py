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
            lista = list(db.kolinja.find({"_id":j['_id']},{"naziv_kolinja":1 , "vaganja.tezina_mesa":1, "vaganja.sol":1, "vaganja.papar":1,"vaganja.ljuta_paprika":1,"vaganja.slatka_paprika":1,"vaganja.bijeli_luk":1,}))
            
            output.append(lista)
       
            
        
        return output
