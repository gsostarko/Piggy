import os
from pymongo import MongoClient

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client.kolinje

class Upiti():
    def filtriranje_vaganja():
        filter = {}
        nazivi = db.kolinja.find(filter)
        vaganja = db.vaganje.find(filter)
        popis_kolinja = []
        popis_id_klanja = []
        vaga = []
        
        for popis in nazivi:
            popis_kolinja.append(popis)
        for i in range(len(popis_kolinja)):
            popis_id_klanja.append(popis_kolinja[i]['_id'])
        #print(popis_id_klanja[0])

        for vag in vaganja:
            vaga.append(vag)
        
        for i in range(len(vaga)):
            for j in range(len(popis_kolinja)):
                print(popis_id_klanja[j])
                print(vaga[i]['id_kolinja'])
                if popis_id_klanja[j] == vaga[i]['id_kolinja']:
                    print('test')
                    #print(vaga['id_kolinja'])


        

        return popis_kolinja