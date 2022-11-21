from flask import Flask, render_template, flash, jsonify, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, PasswordField, BooleanField, ValidationError

from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import pymongo
import datetime 



#client = pymongo.MongoClient("mongodb+srv://gsostarko:mmsw.32E@cluster0.adehxey.mongodb.net/?retryWrites=true&w=majority")
client = pymongo.MongoClient("mongodb://mongo:wvVg7SpdTrlt4RC1Z844@containers-us-west-117.railway.app:6622")

db = client['kolinje']

#collections
recepture = db['recepture']
korisnici = db['korisnici']
termin_kolinja = db['termin_kolinja']




#Create a flask instance
app = Flask(__name__)


# Add Database
app.secret_key = "72feWvvsBCi25kvXqY"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# GLOBALNE VARIJABLE
preracunata_sol =None
preracunati_papar = None
preracunata_lj_paprika = None
preracunata_s_paprika = None
preracunat_luk = None
uk_smjese = None


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
    return recepture.insert_one(document)

def user_registration(username, email, password):
    user = {
        'username': username,
        'email': email,
        'password': password,
        'datum_registracije': datetime.datetime.now()
    }

    return korisnici.insert_one(user)



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


class DodavanjePoljaForma(FlaskForm):
    dodaj_polje=SubmitField("+")

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


@login_manager.user_loader
def load_user(id):
    db = client.get_database('kolinje')
    collection = db.get_collection('korisnici')
    filter = {}

    podaci = collection.find(filter)
    korisnici_temp = []
    for each_doc in podaci:
        korisnici_temp.append(each_doc)
    #print(korisnici_temp)
    if korisnici_temp:
        username = korisnici_temp[0]['username']
        password = korisnici_temp[0]['_id']
        return User(username,password)

# Create a rout decorator
@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/novo_mjerenje/<id>+<naslov_recepta>+<sol>+<papar>+<ljuta_paprika>+<slatka_paprika>+<bijeli_luk>',methods=['GET', 'POST'])

def novo_mjerenje(id,sol, papar, ljuta_paprika, slatka_paprika, bijeli_luk, naslov_recepta):
    global broj_polja
    
    naslov_recepta = None
    kolicina_mesa = None
    meso = 0
    forma_izracun = IzracunForm()
    dodaj_polje = DodavanjePoljaForma()
    
    
    if request.method == 'GET':   
        db = client.get_database('kolinje')
        collection = db.get_collection('recepture')
        id=id
        filter = {}
        
        podaci = collection.find(filter)
        print(naslov_recepta)

        for recept in podaci:
            if str(recept['_id']) == id:
                sol = recept['Sol']
                papar = recept['Papar']
                ljuta_paprika = recept['Ljuta_paprika']
                slatka_paprika = recept['Slatka_paprika']
                bijeli_luk = recept['Bijeli_luk']
                
                naslov_recepta = recept['Naslov_recepta']
                broj_polja = 1
               

                return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa, dodaj_polje=dodaj_polje, broj_polja=broj_polja)

    
    if request.method == "POST":
        
        if request.form["action"]=="Izračunaj":
            print(naslov_recepta)
            global preracunata_sol
            global preracunati_papar 
            global preracunata_lj_paprika 
            global preracunata_s_paprika 
            global preracunat_luk 
            global uk_smjese
            

            
            for i in range(broj_polja):
                 meso += int(request.values[str(i)])
            print(type(meso))
            
            #meso = request.values['0']
            #print(request.values)
            preracunata_sol = float(meso) * float(sol) /100
            preracunati_papar = float(meso) * float(papar) /100
            preracunata_lj_paprika = float(meso) * float(ljuta_paprika) /100
            preracunata_s_paprika = float(meso) * float(slatka_paprika) /100
            preracunat_luk = float(meso) * float(bijeli_luk) / 100
            uk_smjese = float(meso) + preracunata_sol + preracunati_papar + preracunata_lj_paprika + preracunata_s_paprika + preracunat_luk
            return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, uk_smjese=uk_smjese, dodaj_polje=dodaj_polje, broj_polja=broj_polja)

        if request.form["action"] == "+":
            
            
            if list(request.form)[0] == 'action':
                
                broj_polja = broj_polja +1
            
            print(broj_polja)
           
            
            return render_template('novo_mjerenje.html', id=id, naslov_recepta=naslov_recepta, sol=sol, papar=papar, ljuta_paprika=ljuta_paprika, slatka_paprika=slatka_paprika, bijeli_luk=bijeli_luk, forma_izracun=forma_izracun, kolicina_mesa=kolicina_mesa,preracunata_sol=preracunata_sol, preracunati_papar=preracunati_papar, preracunata_lj_paprika=preracunata_lj_paprika,preracunata_s_paprika=preracunata_s_paprika, preracunat_luk=preracunat_luk, uk_smjese=uk_smjese, dodaj_polje=dodaj_polje, broj_polja=broj_polja)



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
    db = client.get_database('kolinje')
    collection = db.get_collection('recepture')
    filter = {}

    podaci = collection.find(filter)
    recepti_temp = []
    for each_doc in podaci:
         recepti_temp.append(each_doc)
         #print(recepti_temp)
    #print(recepti_temp)

    return render_template('popis_recepata.html', recepti_temp=recepti_temp)

@app.route('/registracija', methods=['GET', 'POST'])
def registracija():
    username = None
    email = None
    password = None
    password_confirm = None
    form = RegistrationForm()
    
    db = client.get_database('kolinje')
    collection = db.get_collection('korisnici')
    filter = {}

    podaci = collection.find(filter)
    korisnici_temp = []
    for each_doc in podaci:
        korisnici_temp.append(each_doc)
    #print(korisnici_temp)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        password_confirm = form.password_confirm.data

        #print(password, password_confirm)

        
        ### REGISTRACIJSKI DIO FUNKCIJE I SPREMANJE U BAZU
        if password != password_confirm:
            flash('Passwords don\'t match.', category="error")
            return redirect('registracija')
        
        else:
            db = client.get_database('kolinje')
            collection = db.get_collection('korisnici')
            filter = {'username': username}

            podaci = collection.find(filter)
            korisnici_temp = []
            for each_doc in podaci:
                korisnici_temp.append(each_doc)

            if korisnici_temp:
                for i in range(len(korisnici_temp)):
                    if korisnici_temp[i]['username'] == username:
                        flash(f'Korisnik s korisničkim imenom {username} već postoji.')
                        return redirect('registracija')
                        
                    else:
                        user_registration(username, email, password=generate_password_hash(password, method="sha256"))
                        #print("test")
                        
                        flash(f'Račun s korisničkim imenom: {username} je uspješno kreiran.')
                        
                        return redirect('registracija')
            else: 
                user_registration(username, email, password=generate_password_hash(password, method="sha256"))
                #print("test")
                flash(f'Račun s korisničkim imenom: {username} je uspješno kreiran.')
                return redirect('registracija')

     
            
        
        
    return render_template('registracija.html', username=username, password=password, password_confirm=password_confirm, form=form, korisnici_temp = korisnici_temp)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    form = RegistrationForm()
    username_to_update = None
    #print(id)

@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', user=current_user)  





if __name__ == '__main__':
    app.run(debug = 'DEBUG', host='0.0.0.0', port=80)
    #app.run()
