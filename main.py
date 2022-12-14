import os
from flask import Flask, render_template, flash, jsonify, redirect, request, session, abort, url_for, make_response, send_from_directory
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
import pdfkit

### Custom libraries
from db_querry import Upiti
from izracuni import Izracuni

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
popis_kolinja = []
meso = 0
broj_polja = 1
izracun={}

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
    _id = ObjectId(id_kolinja)
    vaganje = {
        'id_kolinja': id_kolinja,
        'id_vaganja': ObjectId(),
        'sol': sol,
        'papar': papar,
        'ljuta_paprika': ljuta_paprika,
        'slatka_paprika': slatka_paprika,
        'bijeli_luk': bijeli_luk,
        'tezina_mesa': tezina_mesa
    }
    return app.db.kolinja.update_one({"_id": _id}, {"$addToSet": {'vaganja': vaganje}})
    #app.db.vaganje.insert_one(vaganje),


class LoginForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()],render_kw={"placeholder": "korisni??ko ime"})
    password =PasswordField("password", validators = [DataRequired()],render_kw={"placeholder": "lozinka"})
    login = SubmitField("Prijavi se")

class RegistrationForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()],render_kw={"placeholder": "korisni??ko ime"})
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
    
    kolicina_mesa = FloatField("kolicina_mesa", validators = [DataRequired()],render_kw={"placeholder": "koli??ina mesa u gramima"})
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

##### NOVO MJERENJE PROBA


@app.route('/novo_mjerenje/<id>',methods=['GET', 'POST'])
def novo_mjerenje(id):
    filter = {'_id': ObjectId(id)}
    nazivi = app.db.recepture.find(filter)
    
    klanje = []
    for each_doc in nazivi:
        klanje.append(each_doc)
    global broj_polja
    global temp_value
    global uk_smjese
    global meso
    global izracun
    
    temp_value = []   

    filter = {}
    nazivi = app.db.kolinja.find(filter)
    popis_kolinja = []
    for each_doc in nazivi:
        
        popis_kolinja.append(each_doc)
    print(popis_kolinja)
    if request.method == "POST":
        
        if request.form["action"] == "+":
            
            
            values = request.values
            if list(request.form)[0] == 'action': 
                broj_polja = broj_polja +1
                if broj_polja > 5:
                    broj_polja = 5
                    flash("Dosegnuli ste maksimalan broj polja (5)", category="danger")
            temp_value = []
            for i in range(broj_polja-1):
                temp_value.insert(i, values[str(i)])
                
            
            
            return render_template('novo_mjerenje.html', klanje=klanje,temp_value=temp_value, broj_polja=broj_polja,izracun=izracun, uk_smjese=uk_smjese, popis_kolinja=popis_kolinja)

        if request.form["action"] == "-":
            
            if list(request.form)[0] == 'action': 
                broj_polja = broj_polja -1
                if broj_polja < 1:
                    broj_polja = 1
            
            return render_template('novo_mjerenje.html', klanje=klanje,temp_value=temp_value, broj_polja=broj_polja,izracun=izracun, uk_smjese=uk_smjese, popis_kolinja=popis_kolinja)
        
        if request.form["action"]=="Izra??unaj":
            global meso
            for i in range(broj_polja):
                if request.values[str(i)]=='':
                    meso_temp = 0
                else:
                    meso_temp = int(request.values[str(i)])
                meso += meso_temp

            popis_zacina=list(klanje)
            izracun = Izracuni.IzracunVaganja(sol=popis_zacina[0].get('Sol'), papar=popis_zacina[0].get('Papar'), ljuta_paprika=popis_zacina[0].get('Ljuta_paprika'), slatka_paprika=popis_zacina[0].get('Slatka_paprika'), bijeli_luk=popis_zacina[0].get('Bijeli_luk'),meso=meso)

            print(izracun)    
            sastojci = 0
            for i in izracun:
                sastojci += izracun[i]
            uk_smjese = meso + sastojci
            print(uk_smjese) 
              
            broj_polja = 1
            
            
            return render_template('novo_mjerenje.html', klanje=klanje,temp_value=temp_value, broj_polja=broj_polja, izracun=izracun, uk_smjese=uk_smjese, popis_kolinja=popis_kolinja)

        
        if request.form["action"] == "Spremi":
            
            id_kolinja = request.form.get('odabir_klanja')
            
            if id_kolinja == None or id_kolinja == "Odaberite kolinje...":
                
                
                flash("Mjerenje niste dodijelili niti jednom kolinju. Odaberite kolinje te poku??ajte ponovno spremiti mjerenje.", category="danger")

                

                return render_template('novo_mjerenje.html', klanje=klanje,temp_value=temp_value, broj_polja=broj_polja, izracun=izracun, uk_smjese=uk_smjese, popis_kolinja=popis_kolinja)

            elif id_kolinja != None or id_kolinja != "Odaberite kolinje...": 
                popis_zacina=list(klanje)
                print(popis_zacina)
                vaganje(id_kolinja=id_kolinja,sol=popis_zacina[0].get('Sol'), papar=popis_zacina[0].get('Papar'), ljuta_paprika=popis_zacina[0].get('Ljuta_paprika'), slatka_paprika=popis_zacina[0].get('Slatka_paprika'), bijeli_luk=popis_zacina[0].get('Bijeli_luk'),tezina_mesa=meso)
                
                
                flash("Uspje??no ste pohranili novo mjerenje.", category="warning")
                
                return redirect(f'{id}')
                

        
    
    else: 
        uk_smjese = None
        meso = 0
    return render_template('novo_mjerenje.html', klanje=klanje,broj_polja=broj_polja, temp_value=temp_value,izracun=izracun, uk_smjese=uk_smjese, popis_kolinja=popis_kolinja)



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
                flash(f'Uspje??no ste se prijavili kao {loged_in_user}', category='success')

                test = login_user(user, remember=True)
                #print(test)
                return redirect('dashboard')

            else:
                flash('Korisni??ko ime ili lozinka nisu ispravni. Poku??ajete ponovno', category='error')
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
        flash("Recept je uspje??no pohranjen!")
        
        
        
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
    
    print(id)
    print(recept)
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

        return redirect('/popis_recepata')
    return redirect('/popis_recepata')

@app.route('/brisanje_recepta/<id>', methods=['POST', 'GET'])
def brisanje_recepta(id):
    
    app.db.recepture.delete_one({'_id': ObjectId(id)})
    

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

        return redirect('/pregled_kolinja')
    
    return render_template('pregled_kolinja.html', vaganje_temp=vaganje_temp, printer=printer)

@app.route('/brisanje_kolinja/<id>', methods=['POST', 'GET'])
def brisanje_kolinja(id):
    
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

    app.db.kolinja.delete_one({'_id': ObjectId(id)})

    return redirect('/pregled_kolinja')
    

@app.route('/edit_kolinja/<id><idx>', methods=['GET','POST'])
def edit_kolinja(id,idx):
    print(id)
    print(idx)

    filter = {'_id': ObjectId(id)}
    nazivi = app.db.kolinja.find(filter)
    popis_kolinja = []
    for popis in nazivi:
        popis_kolinja.append(popis)
    print(popis_kolinja)

    return redirect('/pregled_kolinja')

@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users[username] = password
        password_confirm = request.form.get("password_confirm")
        
        session["username"] = username

    return render_template('registracija.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', user=session.get("username"))  

app.get("/protected")
def protected():
    if not session.get("_id"):
        abort(401)
    return render_template("protected.html")


@app.route('/pdf_kolinja/<id>')
def pdf_kolinja(id):
    # rendered = render_template('pdf_kolinja.html')
    # pdf = pdfkit.from_string(rendered, False)

    import pdf
    pdf.pdf_kolinja(id)
    
    return send_from_directory(directory='static/pdf_temp',
                                path='kolinje.pdf',
                                mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug = 'DEBUG', host='0.0.0.0', port=80)
    
