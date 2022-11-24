import os
from flask import Flask, render_template, flash, jsonify, redirect, request, session, abort, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField, BooleanField, ValidationError

from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime 

from db_querry import Upiti

load_dotenv()

app = Flask(__name__)

#client = MongoClient("mongodb+srv://gsostarko:mmsw.32E@cluster0.adehxey.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(os.environ.get("MONGODB_URI"))

app.db = client.kolinje

#collections
#recepture = db['recepture']
#korisnici = db['korisnici']
#termin_kolinja = db['termin_kolinja']




#Create a flask instance



# Add Database
app.secret_key = os.environ.get("SECRET_KEY")




# GLOBALNE VARIJABLE
preracunata_sol =None
preracunati_papar = None
preracunata_lj_paprika = None
preracunata_s_paprika = None
preracunat_luk = None
uk_smjese = None
temp_value = []
users = {}
popis_kolinja = {}
meso = 0

##DB insert model
def add_recepie(naziv_recepta,sol, papar, bijeli_luk, ljuta_paprika, slatka_paprika):
    document = {
        'Naslov_recepta': naziv_recepta,
        'Sol': sol,
        'Papar': papar,
        'Bijeli_luk': bijeli_luk,
        'Ljuta_paprika' : ljuta_paprika,
        'Slatka_paprika': slatka_paprika,
        'Datum_kreiranja' : datetime.datetime.now()
    }
    return app.db.recepture.insert_one(document)

def user_registration(username, email, password):
    user = {
        'username': username,
        'email': email,
        'password': password,
        'datum_registracije': datetime.datetime.now()
    }

    return app.db.korisnici.insert_one(user)

def kolinje(naziv_kolinja):
    kolinje = {
        'naziv_kolinja': naziv_kolinja
    }
    return app.db.kolinja.insert_one(kolinje)

def vaganje(id_kolinja,sol,papar,ljuta_paprika,slatka_paprika,bijeli_luk,tezina_mesa):
    vaganje = {
        'id_kolinja': id_kolinja,
        'sol': sol,
        'papar': papar,
        'ljuta_paprika': ljuta_paprika,
        'slatka_paprika': slatka_paprika,
        'bijeli_luk': bijeli_luk,
        'tezina_mesa': tezina_mesa
    }
    return app.db.vaganje.insert_one(vaganje)


class LoginForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()],render_kw={"placeholder": "korisničko ime"})
    password =PasswordField("password", validators = [DataRequired()],render_kw={"placeholder": "lozinka"})
    login = SubmitField("Prijavi se")

class RegistrationForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()],render_kw={"placeholder": "korisničko ime"})
    email = StringField("email", validators = [DataRequired()],render_kw={"placeholder": "email"})
    password =PasswordField("password", validators = [DataRequired()],render_kw={"placeholder": "lozinka"})
    password_confirm=PasswordField("password_confirm", validators = [DataRequired()],render_kw={"placeholder": "potvrda lozinke"})
    register = SubmitField("Registriraj se")
    
class ReceptiForm(FlaskForm):
    naziv_recepta = StringField("naziv_recepta", validators = [DataRequired()],render_kw={"placeholder": "naziv recepta"})
    sol = FloatField("sol", validators = [DataRequired()],render_kw={"placeholder": "sol"})
    papar = FloatField("papar", validators = [DataRequired()],render_kw={"placeholder": "papar"})
    slatka_paprika = FloatField("slatka_paprika", validators = [DataRequired()],render_kw={"placeholder": "slatka paprika"})
    ljuta_paprika = FloatField("ljuta_paprika", validators = [DataRequired()],render_kw={"placeholder": "ljuta paprika"})
    bijeli_luk = FloatField("bijeli_luk", validators = [DataRequired()],render_kw={"placeholder": "bijeli luk"})
    spremi_recept = SubmitField("Spremi")

class IzracunForm(FlaskForm):
    
    kolicina_mesa = FloatField("kolicina_mesa", validators = [DataRequired()],render_kw={"placeholder": "količina mesa u gramima"})
    izracunaj = SubmitField("Izracunaj")




class User(UserMixin):
    def __init__(self, username, id, active=True):
        self.username = username
        self.id = id
        self.active = active
    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True



# Create a rout decorator
@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/novo_mjerenje/<id>+<naslov_recepta>+<sol>+<papar>+<ljuta_paprika>+<slatka_paprika>+<bijeli_luk>',methods=['GET', 'POST'])

def novo_mjerenje(id,sol, papar, ljuta_paprika, slatka_paprika, bijeli_luk, naslov_recepta):
    global broj_polja

    
    kolicina_mesa = None
    
    forma_izracun = IzracunForm()
    global temp_value
    
    filter = {}
    nazivi = app.db.kolinja.find(filter)
    popis_kolinja = []
    for each_doc in nazivi:
        popis_kolinja.append(each_doc)
    
    if request.method == 'GET':   
        db = client.get_database('kolinje')
        collection = db.get_collection('recepture')
        id=id
        filter = {}
        
        podaci = collection.find(filter)
        

        for recept in podaci:
            if str(recept['_id']) == id:
                sol = recept['Sol']
                papar = recept['Papar']
                ljuta_paprika = recept['Ljuta_paprika']
                slatka_paprika = recept['Slatka_paprika']
                bijeli_luk = recept['Bijeli_luk']
                
                naslov_recepta = recept['Naslov_recepta']
                broj_polja = 1
               

                return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa, broj_polja=broj_polja,temp_value=temp_value, popis_kolinja=popis_kolinja)

    
    if request.method == "POST":
        
        sol=sol
        papar = papar
        ljuta_paprika = ljuta_paprika
        slatka_paprika = slatka_paprika 
        bijeli_luk = bijeli_luk
        global meso
        id_kolinja = None
        temp_kolinje = ""
        if request.form["action"]=="Izračunaj":
            
            global preracunata_sol
            global preracunati_papar 
            global preracunata_lj_paprika 
            global preracunata_s_paprika 
            global preracunat_luk 
            global uk_smjese
            
            
            
            for i in range(broj_polja):
                if request.values[str(i)]=='':
                    meso_temp = 0
                else:
                    meso_temp = int(request.values[str(i)])
                meso += meso_temp
            
            
            preracunata_sol = float(meso) * float(sol) /100
            preracunati_papar = float(meso) * float(papar) /100
            preracunata_lj_paprika = float(meso) * float(ljuta_paprika) /100
            preracunata_s_paprika = float(meso) * float(slatka_paprika) /100
            preracunat_luk = float(meso) * float(bijeli_luk) / 100
            preracunata_sol = round(preracunata_sol,1)
            preracunati_papar= round(preracunati_papar,1)
            preracunata_lj_paprika = round(preracunata_lj_paprika,1)
            preracunata_s_paprika = round(preracunata_s_paprika,1)
            preracunat_luk = round(preracunat_luk,1)
            uk_smjese = float(meso) + preracunata_sol + preracunati_papar + preracunata_lj_paprika + preracunata_s_paprika + preracunat_luk
            uk_smjese = round(uk_smjese, 1)
            broj_polja = 1
            temp_value = []
            
            
            
            
            return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, uk_smjese=uk_smjese, broj_polja=broj_polja,temp_value=temp_value,  popis_kolinja=popis_kolinja, meso=meso,temp_kolinje=temp_kolinje)

        if request.form["action"] == "Spremi":
            
            id_kolinja = request.form.get('odabir_klanja')
            
            if id_kolinja == None or id_kolinja == "Odaberite kolinje...":
                
                
                flash("Mjerenje niste dodijelili niti jednom kolinju. Odaberite kolinje te pokušajte ponovno spremiti mjerenje.", category="danger")
                
                return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, broj_polja=broj_polja,temp_value=temp_value,  popis_kolinja=popis_kolinja,temp_kolinje=temp_kolinje, uk_smjese=uk_smjese)

            else:
                temp_kolinje = id_kolinja
                print(temp_kolinje)
                vaganje(id_kolinja=id_kolinja,sol=sol,papar=papar,ljuta_paprika=ljuta_paprika,slatka_paprika=slatka_paprika,bijeli_luk=bijeli_luk,tezina_mesa=meso)
                broj_polja = 1
                temp_value=[]
                meso = 0
                
                flash("Uspješno ste pohranili novo mjerenje.", category="warning")
                return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, broj_polja=broj_polja,temp_value=temp_value,  popis_kolinja=popis_kolinja, temp_kolinje=temp_kolinje, meso=meso)

        if request.form["action"] == "+":
            
            values = request.values
            if list(request.form)[0] == 'action': 
                broj_polja = broj_polja +1
                if broj_polja > 5:
                    broj_polja = 5
                print(list(request.form)[1])
            #print(broj_polja)
            temp_value = []
            for i in range(broj_polja-1):
                print(i)
                print(values[str(i)])
                temp_value.insert(i, values[str(i)])
            

            return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, uk_smjese=uk_smjese, broj_polja=broj_polja,temp_value=temp_value,  popis_kolinja=popis_kolinja, meso=meso,temp_kolinje=temp_kolinje)


            
            

        if request.form["action"] == "-":
            
            if list(request.form)[0] == 'action': 
                broj_polja = broj_polja -1
                if broj_polja < 1:
                    broj_polja = 1
            #print(broj_polja)
            return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, uk_smjese=uk_smjese, broj_polja=broj_polja,temp_value=temp_value,  popis_kolinja=popis_kolinja, meso=meso,temp_kolinje=temp_kolinje)
broj_polja_ = 0
@app.route('/test',methods=['GET', 'POST'])
def test():
    global broj_polja

    broj_polja = broj_polja +1 
    
    print(test)
    return render_template('test.html', broj_polja=broj_polja)

@app.route('/login',methods=['GET', 'POST'])
def login():
    username = None
    password = None
    forma_prijava = LoginForm()

    if forma_prijava.validate_on_submit():

        username = forma_prijava.username.data
        password = forma_prijava.password.data
        #print(username)
        #print(password)

        db = client.get_database('kolinje')
        collection = db.get_collection('korisnici')
        filter = {'username': username}

        podaci = collection.find(filter)
        korisnici_temp = []
        for each_doc in podaci:
            korisnici_temp.append(each_doc)

        #print(korisnici_temp[0])
        if korisnici_temp:
            loged_in_user = korisnici_temp[0]['username']

        #print(jsonify(korisnici_temp[0]))
        user = User(korisnici_temp[0]['username'], korisnici_temp[0]['_id'])
        if korisnici_temp:
            if check_password_hash(korisnici_temp[0]['password'], password):
                flash(f'Uspješno ste se prijavili kao {loged_in_user}', category='success')

                test = login_user(user, remember=True)
                #print(test)
                return redirect('dashboard')

            else:
                flash('Korisničko ime ili lozinka nisu ispravni. Pokušajete ponovno', category='error')
        else:
            flash('Korisnik ne postoji', category='error')

    return render_template('login.html', forma_prijava=forma_prijava, username = username, password = password)

@app.route('/recepti',methods=['GET', 'POST'])
def recepti():
    naziv_recepta = None
    sol = None
    papar = None
    ljuta_paprika = None
    slatka_paprika = None
    bijeli_luk = None
    forma_recepti = ReceptiForm()

    if forma_recepti.validate_on_submit():
        naziv_recepta = forma_recepti.naziv_recepta.data
        sol = forma_recepti.sol.data
        papar = forma_recepti.papar.data
        ljuta_paprika= forma_recepti.ljuta_paprika.data
        slatka_paprika= forma_recepti.slatka_paprika.data
        bijeli_luk=forma_recepti.bijeli_luk.data
        add_recepie(naziv_recepta, sol, papar, bijeli_luk, ljuta_paprika, slatka_paprika)
        flash("Recept je uspješno pohranjen!")
        
        
        
        return redirect('popis_recepata')
   
    return render_template('recepti.html', naziv_recepta=naziv_recepta, sol=sol,papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, forma_recepti=forma_recepti,)

@app.route('/popis_recepata',methods=['GET', 'POST'])
def popis_recepata():
    filter = {}

    podaci = app.db.recepture.find(filter)
    recepti_temp = []
    for each_doc in podaci:
         recepti_temp.append(each_doc)
    

    return render_template('popis_recepata.html', recepti_temp=recepti_temp)

@app.route('/azuriranje_recepta/<id>', methods=['POST', 'GET'])
def azuriranje_recepta(id):
    
    
    filter = {}
        
    podaci = app.db.recepture.find(filter)
    

    for recept in podaci:
        if str(recept['_id']) == id:
            recept=recept
            break
    

    if request.method == 'POST':
        edited_id= request.form.get("edited_id")
        edited_sol = float(request.form.get("edited_sol"))
        edited_papar = float(request.form.get("edited_papar"))
        edited_slatka_paprika = float(request.form.get("edited_slatka_paprika"))
        edited_ljuta_paprika = float(request.form.get("edited_ljuta_paprika"))
        edited_bijeli_luk = float(request.form.get("edited_bijeli_luk"))
        edited_date = datetime.datetime.now()
        
        data_for_update = {
            "$set": {"Sol": float(edited_sol),
            "Papar": edited_papar,
            "Slatka_paprika": edited_slatka_paprika,
            "Ljuta_paprika": edited_ljuta_paprika,
            "Bijeli_luk": edited_bijeli_luk,
            "Update_date": edited_date}
        }
        
        update = app.db.recepture.update_one({'_id': ObjectId(id)}, data_for_update)
        #print(update.matched_count)

        filter = {}

        podaci = app.db.recepture.find(filter)
        recepti_temp = []
        for each_doc in podaci:
            recepti_temp.append(each_doc)

        return render_template('popis_recepata.html', recepti_temp=recepti_temp)
    return render_template('azuriranje_recepta.html', recept=recept)

@app.route('/brisanje_recepta/<id>', methods=['POST', 'GET'])
def brisanje_recepta(id):
    
    app.db.recepture.delete_one({'_id': ObjectId(id)})
    print(id)

    filter = {}

    podaci = app.db.recepture.find(filter)
    recepti_temp = []
    for each_doc in podaci:
        recepti_temp.append(each_doc)

    return render_template('popis_recepata.html', recepti_temp=recepti_temp)



@app.route('/pregled_kolinja', methods=['GET', 'POST'])
def popis_kolinja():
    filter = {}
    nazivi = app.db.kolinja.find(filter)
    vaganja = app.db.vaganje.find(filter)
    popis_kolinja = []
    
    for popis in nazivi:
        popis_kolinja.append(popis)

    vaganje_temp=[]
    for each_doc in vaganja:
        vaganje_temp.append(each_doc)
    
    #FUNKCIJA ZA FILTRIRANJE PODATAKA
    printer = Upiti.filtriranje_vaganja()
    



    if request.method == 'POST':
        naziv_kolinja = request.form.get("naziv_kolinja")
        kolinje(naziv_kolinja)

    
    return render_template('pregled_kolinja.html', vaganje_temp=vaganje_temp)


@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users[username] = password
        password_confirm = request.form.get("password_confirm")
        
        session["username"] = username

    return render_template('registracija.html')

    # username = None
    # email = None
    # password = None
    # password_confirm = None
    # form = RegistrationForm()
    
    # db = client.get_database('kolinje')
    # collection = db.get_collection('korisnici')
    # filter = {}

    # podaci = collection.find(filter)
    # korisnici_temp = []
    # for each_doc in podaci:
    #     korisnici_temp.append(each_doc)
    # #print(korisnici_temp)

    # if form.validate_on_submit():
    #     username = form.username.data
    #     email = form.email.data
    #     password = form.password.data
    #     password_confirm = form.password_confirm.data

    #     #print(password, password_confirm)

        
    #     ### REGISTRACIJSKI DIO FUNKCIJE I SPREMANJE U BAZU
    #     if password != password_confirm:
    #         flash('Passwords don\'t match.', category="error")
    #         return redirect('registracija')
        
    #     else:
    #         db = client.get_database('kolinje')
    #         collection = db.get_collection('korisnici')
    #         filter = {'username': username}

    #         podaci = collection.find(filter)
    #         korisnici_temp = []
    #         for each_doc in podaci:
    #             korisnici_temp.append(each_doc)

    #         if korisnici_temp:
    #             for i in range(len(korisnici_temp)):
    #                 if korisnici_temp[i]['username'] == username:
    #                     flash(f'Korisnik s korisničkim imenom {username} već postoji.')
    #                     return redirect('registracija')
                        
    #                 else:
    #                     user_registration(username, email, password=generate_password_hash(password, method="sha256"))
    #                     #print("test")
                        
    #                     flash(f'Račun s korisničkim imenom: {username} je uspješno kreiran.')
                        
    #                     return redirect('registracija')
    #         else: 
    #             user_registration(username, email, password=generate_password_hash(password, method="sha256"))
    #             #print("test")
    #             flash(f'Račun s korisničkim imenom: {username} je uspješno kreiran.')
    #             return redirect('registracija')

     
            
        
        
    # return render_template('registracija.html', username=username, password=password, password_confirm=password_confirm, form=form, korisnici_temp = korisnici_temp)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', user=current_user)  

app.get("/protected")
def protected():
    if not session.get("_id"):
        abort(401)
    return render_template("protected.html")



if __name__ == '__main__':
    app.run(debug = 'DEBUG', host='0.0.0.0', port=80)
    
