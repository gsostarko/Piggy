from flask import Flask, render_template, flash, redirect, request
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SECRET_KEY'] = "72feWvvsBCi25kvXqY"



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
    document = {
        'username': username,
        'email': email,
        'password': password,
        'datum_registracije': datetime.datetime.now()
    }

    return korisnici.insert_one(document)




class RegistrationForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()],render_kw={"placeholder": "korisničko ime"})
    email = StringField("email", validators = [DataRequired()],render_kw={"placeholder": "email"})
    password =PasswordField("password", validators = [DataRequired(), EqualTo('password_confirm', message='Lozinke moraju biti jednake')],render_kw={"placeholder": "lozinka"})
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

# Create a rout decorator
@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
         print(recepti_temp)
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
        email=form.email.data
        password = form.password.data
        password_confirm = form.password_confirm.data

        print(password, password_confirm)

        

        if password == password_confirm :
            user_registration(username, email, password)
            print("test")
            
            return redirect('registracija')

        else:
            flash("error: nisu identične lozinke")
     
            
        
        
    return render_template('registracija.html', username=username, password=password, password_confirm=password_confirm, form=form, korisnici_temp = korisnici_temp)

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    form = RegistrationForm()
    username_to_update = None
    print(id)
    
#Create a form class



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    #app.run()
