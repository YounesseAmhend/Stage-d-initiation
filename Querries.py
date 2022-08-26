from neo4j import GraphDatabase

# API to connect us to the database
uri = "bolt://localhost:7687"
drivers = GraphDatabase.driver(uri, auth=("neo4j", "mdm"))

# functions to create database
def cree_employe(tx,etablissement, nom, prenom, date_naissance, genre, situation_familiale, adresse, numero_telephone, email, fonctionalite,salaire, date_embauche):
    tx.run("match (etab:ETABLISSEMENT {Nom_etablissment: $etablissement})"                                      
           "create (:EMPLOYEUR {Nom: $nom, Prenom: $prenom, Date_naissance:$date_naissance, Genre:$genre,"
           "Situation_familiale:$situation_familiale, Adresse:$adresse, Numero_telephone: $numero_telephone,Email:$email, Fonctionalite: $fonctionalite, Date_embauche:$date_embauche, salaire: $salaire})-[:Travail_pour]->(etab)", 
           etablissement=etablissement, nom=nom, prenom=prenom, date_naissance=date_naissance,
           genre=genre, situation_familiale=situation_familiale, adresse=adresse,email=email,
           fonctionalite=fonctionalite, numero_telephone=numero_telephone, salaire=salaire,date_embauche=date_embauche)

def cree_etablissement(tx, Nom_etablissment, adresse, email, numero_telephone, site_web, password):
    tx.run("create(:ETABLISSEMENT {Nom_etablissment:$Nom_etablissment, adresse:$adresse, email:$email,"
           "numero_telephone:$numero_telephone, site_web:$site_web, password:$password})"
           , Nom_etablissment=Nom_etablissment, adresse=adresse, email=email, numero_telephone=numero_telephone, site_web=site_web, password=password)
    
def prime(tx, Nom, Prenom, motif, montant, date):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
    "Create(P:Prime{motif:$motif, montant:$montant, date:$date}),"
    "(e)-[:récompensé]->(P)"
    , Nom=Nom, Prenom=Prenom, motif=motif, montant=montant, date=date)
    
def travail_suplementaire(tx, Nom, Prenom, date, nombre_heure):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
        "Create(s:Heur_Suplementaire {date:$date, nombre_heure:$nombre_heure}),"
        "(e)-[:Suplementer]->(s)",
        Nom=Nom, Prenom=Prenom, date=date, nombre_heure=nombre_heure)

def conje(tx, Nom, Prenom, Date_debut, Date_Fin, Motif, nombre):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
           "Create(c:CONJE {Date_debut:$Date_debut, Date_Fin:$Date_Fin, Motif:$Motif, Nombre_jour:$nombre}),"
           "(e)-[:conje]->(c)",
           Nom=Nom, Prenom=Prenom, Date_debut=Date_debut, Date_Fin=Date_Fin, Motif=Motif, nombre=nombre)
    
def absence(tx, Nom, Prenom, date_debut, date_fin, Motif, Justifie, nombre):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
           "Create(a:ABSENCE {date_debut:$date_debut, date_fin:$date_fin, Motif:$Motif, Justifie:$Justifie, Nombre_jour:$nombre}),"
           "(e)-[:Absente]->(a)",
           Nom=Nom, Prenom=Prenom, date_debut=date_debut, date_fin=date_fin, Motif=Motif, Justifie=Justifie, nombre=nombre)
    
def licencier(tx, Nom, Prenom, date_fin_embauche):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
           "REMOVE e:EMPLOYEUR SET e:LIENCE, e.date_fin_embauche =$date_fin_embauche",
            Nom=Nom, Prenom=Prenom, date_fin_embauche=date_fin_embauche)
    
def tache(tx, Nom, Prenom, date_limite, Description):
    tx.run("match(e:EMPLOYEUR {Nom:$Nom, Prenom:$Prenom})"
           "Create(a:TACHE {date_limite:$date_limite, Description:$Description}),"
           "(e)-[:Faire]->(a)",
           Nom=Nom, Prenom=Prenom, date_limite=date_limite, Description=Description)
