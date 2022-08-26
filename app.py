from flask import Flask, redirect, url_for, render_template, request, session, flash, get_flashed_messages
from datetime import datetime, timedelta, date
from flask_session import Session
from Querries import *
from functools import wraps

# good function no touch here
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
def age(date):
    currentDate = datetime.now()
    if currentDate.month > date.month:
        age = currentDate.year - date.year - 1
    elif currentDate.month > date.month:
        age = currentDate.year - date.year
    elif currentDate.month == date.month:
        if currentDate.day > date.day:
            age = currentDate.year - date.year - 1
        else:
            age = currentDate.year - date.year
    return age 
def days(debut,fin):
    d0 = date(debut.year, debut.month, debut.day)
    d1 = date(fin.year, fin.month, fin.day)
    delta = d1 - d0
    return delta.days
#flask app
app = Flask(__name__, static_url_path='/static')
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = drivers.session()

#Admin stuff
@app.route('/')
def home():
    conje = db.run("MATCH (m:EMPLOYEUR)-[:conje]->(n:CONJE) return n,m").data()
    employeur = db.run("MATCH(n:EMPLOYEUR) return n").data()
    absence = db.run("MATCH (m:EMPLOYEUR)-[:Absente]->(n:ABSENCE) return n,m").data()
    return render_template("index.html", employeur=employeur, absence=absence, conje=conje)
#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Posted")
        session.clear()
        nom = request.form.get("Nom").title()
        password = request.form["password"]
        data = db.run("MATCH (N:ETABLISSEMENT {Nom_etablissment:$nom, password:$password}) return N",nom=nom,password=password).data()
        id = db.run("MATCH (N:ETABLISSEMENT {Nom_etablissment:$nom, password:$password}) return ID(N) as id", nom=nom,password=password).data()
        if len(id) == 0:
            flash("Invalid username or password")
            return render_template("loginEtablissement.html")
        session["user_id"] = id[0]["id"]
        return redirect("/")
    else:
        return render_template("loginEtablissement.html")
    
#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.clear()
        Nom_etablissment = request.form["etablissement"].title()
        adresse = request.form["Adresse"]
        email = request.form["Email"]
        numero_telephone = request.form["Numero"]
        site_web = request.form["Site"]
        Password = request.form["Password"]
        db.run("""create(:ETABLISSEMENT {Nom_etablissment:$Nom_etablissment, adresse:$adresse, email:$email,
           numero_telephone:$numero_telephone, site_web:$site_web, password:$password})"""
           , Nom_etablissment=Nom_etablissment, adresse=adresse, email=email, numero_telephone=numero_telephone, site_web=site_web, password=Password)
        id = db.run("MATCH (N:ETABLISSEMENT {Nom_etablissment:$Nom_etablissment, password:$Password}) return ID(N) as id", Nom_etablissment=Nom_etablissment,Password=Password).data()
        session["user_id"] = id[0]["id"]
        return redirect("/")
    else:
        return render_template("/register.html")


@app.route("/employeur", methods=["GET", "POST"])
@login_required
def employeurs():
    if request.method == "POST":
        Nom = request.form["Nom"].title()
        Prenom = request.form["Prenom"].title()
        employeur = db.run("MATCH(n:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom}) return n", Prenom=Prenom, Nom=Nom).data()
        conje = db.run("MATCH(m:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})-[:conje]->(n:CONJE) return n,m", Prenom=Prenom, Nom=Nom).data()
        absence = db.run("MATCH(m:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})-[:Absente]->(n:ABSENCE) return n,m", Prenom=Prenom, Nom=Nom).data()
        return render_template("aficheremployeur.html", employeur=employeur, conje=conje, absence=absence)
    else:
        return render_template("aficherEmployeur.html")
@app.route('/ajouter_employeur', methods=['GET', 'POST'])
@login_required
def ajouter_employeur():
    if request.method == 'POST':
        q  = db.run("MATCH (n:ETABLISSEMENT) return n").data()
        etablissement = q[0]["n"]["Nom_etablissment"]
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Date"] or not request.form["Situation"] or not request.form["Adresse"] or not request.form["DateE"] or not request.form["Numero"] or not request.form["Email"] or not request.form["Fonctionalite"] or not request.form["Salaire"] or not request.form["Genre"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/employeur")
        nom = request.form["Nom"].title()
        prenom = request.form["Prenom"].title()
        q1 = db.run("MATCH (n:EMPLOYEUR {Nom:$nom, Prenom:$prenom}) return n", nom=nom, prenom=prenom).data()
        if len(q1) != 0:
            flash("L'employeur existe déjà")
            return redirect("/employeur")
        date_naissance = request.form["Date"]
        date = datetime.strptime(date_naissance, '%Y-%m-%d')
        print(age(date))
        if age(date) < 18:
            flash("L'employeur n'est pas un adulte")
            return redirect("/employeur")
        situation_familiale= request.form["Situation"]
        adresse = request.form["Adresse"]
        # if len(adresse) <= 10:
        #     flash("Adresse doit etre superieur a 10 characters")
        #     return redirect("/employeur")
        date_embauche = request.form["DateE"]
        currentDate = datetime.now()
        date = datetime.strptime(date_embauche, '%Y-%m-%d')
        if currentDate < date:
            flash("la date d'embauche doit etre inferiuere ou egale a la date actuelle")
            return redirect("/employeur")
        numero_telephone = request.form["Numero"]
        email = request.form["Email"]
        fonctionalite = request.form["Fonctionalite"]
        try:
            salaire = int(request.form["Salaire"])
            if salaire < 2000:
                flash("verifier le salaire")
                return redirect("/employeur")
        except ValueError:
            flash("Le salaire doit etre un entier")
            return redirect("/employeur")
        genre = request.form.get("Genre")
        with drivers.session() as session:
            session.write_transaction(cree_employe, etablissement, nom, prenom, date_naissance, genre, situation_familiale, adresse, numero_telephone, email, fonctionalite, salaire,date_embauche)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/employeur.html")

@app.route("/show", methods=["GET", "POST"])
@login_required
def show():
    q1 = """
    match (n:EMPLOYEUR) return n
    """
    results = drivers.session().run(q1)
    data = results.data()
    return render_template("show.html", data=data)


@app.route("/prime", methods=["GET", "POST"])
@login_required
def primes():
    if request.method == "POST":
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Motif"] or not request.form["Montant"] or not request.form["Date"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/prime")
        Nom = request.form["Nom"].title()
        Prenom = request.form["Prenom"].title()
        motif = request.form["Motif"]
        try:
            montant = int(request.form["Montant"])
            if montant < 0:
                flash("Le montant doit etre ")
                return redirect("/prime")
        except ValueError:
            flash("Le Montant doit etre un entier")
            return redirect("/prime")
        dateP = request.form["Date"]
        currentDate = datetime.now()
        date = datetime.strptime(dateP, '%Y-%m-%d')
        if currentDate < date:
            flash("la date de prime doit etre inferieure ou egale a la date actuelle")
            return redirect("/prime")
        with drivers.session() as session:
            session.write_transaction(prime, Nom, Prenom, motif, montant, dateP)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/primes.html")   


@app.route("/heure_suplementaire", methods=["GET", "POST"])
@login_required
def travail():
    if request.method == "POST":
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Date"] or not request.form["NombreHeure"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/heure_suplementaire")
        Nom = request.form["Nom"]
        Prenom = request.form["Prenom"]
        q = db.run("match(n:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom}) return n", Nom=Nom, Prenom=Prenom).data()
        if len(q) == 0:
            flash("l'employeur n'existe pas")
            return redirect("/heure_suplementaire")
        date = request.form["Date"]
        
        dateD = datetime.strptime(q[0]["n"]["Date_embauche"],'%Y-%m-%d')
        dateF = datetime.strptime(date,'%Y-%m-%d')
        
        if dateD > dateF :
            flash("veirfier la date")
            return redirect("/heure_suplementaire")
        try:
            nombre_heure = float(request.form["NombreHeure"])
            if nombre_heure > 6 or nombre_heure < 0:
                flash("verifier le nombre des heurs")
        except ValueError:
            flash("Nombre d'heures doit etre un réel")
            return redirect("/heure_suplementaire")
        with drivers.session() as session:
            session.write_transaction(travail_suplementaire, Nom, Prenom, date, nombre_heure)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/travail.html")   


@app.route("/conje", methods=["GET", "POST"])
@login_required
def conjes():
    if request.method == "POST":
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Motif"] or not request.form["DateD"] or not request.form["DateF"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/conje")
        Nom = request.form["Nom"].title()
        Prenom = request.form["Prenom"].title()
        q = db.run("match(n:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom}) return n", Nom=Nom, Prenom=Prenom).data()
        if len(q) == 0:
            flash("l'employeur n'existe pas")
            return redirect("/conje")
        Date_debut = request.form["DateD"]
        Date_Fin = request.form["DateF"]
        dateD = datetime.strptime(Date_debut, '%Y-%m-%d') 
        dateF = datetime.strptime(Date_Fin, '%Y-%m-%d')
        dateE = datetime.strptime(q[0]["n"]["Date_embauche"],'%Y-%m-%d')
        if dateE > dateD:
            falsh("verifier la date de debut")
            return redirect("/conje")
        if dateD > dateF:
            flash("La date de debut doit etre inferieure a la date de fin")
            return redirect("/conje")
        Motif = request.form["Motif"]
        with drivers.session() as session:
            session.write_transaction(conje,  Nom, Prenom, Date_debut, Date_Fin, Motif, days(dateD, dateF)+1)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/conje.html")   


@app.route("/absence", methods=["GET", "POST"])
@login_required
def abcences():
    if request.method == "POST":
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Motif"] or not request.form["DateD"] or not request.form["DateF"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/absence")
        Nom = request.form["Nom"].title()
        Prenom = request.form["Prenom"].title()
        q = db.run("match(n:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom}) return n", Nom=Nom, Prenom=Prenom).data()
        if len(q) == 0:
            flash("l'employeur n'existe pas")
            return redirect("/absence")
        date_debut = request.form["DateD"]
        date_fin = request.form["DateF"]
        
        dateD = datetime.strptime(date_debut, '%Y-%m-%d') 
        dateE = datetime.strptime(q[0]["n"]["Date_embauche"],'%Y-%m-%d')
        if dateE > dateD:
            falsh("verifier la date de debut")
            return redirect("/absence")
        dateF = datetime.strptime(date_fin, '%Y-%m-%d')
        if dateD > dateF:
            flash("La date de debut doit etre inferieure a la date de fin")
            return redirect("/absence")
        Motif = request.form["Motif"]
        Justifie = request.form["Justifie"]
        with drivers.session() as session:
            session.write_transaction(absence, Nom, Prenom, date_debut, date_fin, Motif, Justifie, days(dateD, dateF)+1)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/absence.html")   

@app.route("/licencier", methods=["GET", "POST"])
@login_required
def licenciers():
    if request.method == "POST":
        if not request.form["Nom"] or not request.form["Prenom"] or not request.form["Motif"]:
            flash("Assurez-vous de remplir tous les champs")
            return redirect("/licencier")
        Nom = request.form["Nom"].title()
        Prenom = request.form["Prenom"].title()
        
        q = db.run("match(n:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom}) return n", Nom=Nom, Prenom=Prenom).data()
        if len(q) == 0:
            flash("l'employeur n'existe pas")
            return redirect("/licencier")
        
        dateD = datetime.strptime(q[0]["n"]["Date_embauche"],'%Y-%m-%d')
        date_fin_embauche = request.form["DateFin"]
        dateF = datetime.strptime(date_fin_embauche,'%Y-%m-%d')
        
        if dateD > dateF :
            flash("La date d'embauche doit etre inferiuere á la date de licencier")
            return redirect("/licencier")
        with drivers.session() as session:
            session.write_transaction(licencier, Nom, Prenom, date_fin_embauche)
        drivers.close()
        return redirect("/")
    else:
        return render_template("/lience.html")   

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/login")
if __name__ == '__main__':
    app.run(debug=True)
