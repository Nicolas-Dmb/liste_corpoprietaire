import os
import re
from flask import Flask, flash, render_template, request, send_file, url_for, redirect, session
import pandas as pd
import secrets
from test import transform_file
from excel import names_coproprietes, residence_principale
from lots import tri_liste_lot, add_lot
from compare import compare_list
from MP import test_password, remove_file
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, timezone
from flask_login import LoginManager, UserMixin, login_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String


template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask(__name__)
#app.config['SERVER_NAME'] = 'listexcel.fr/' 
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

#stockage des fichiers 
uploads_dir = os.path.join(app.instance_path, 'files')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

#Gestion de la base de données avec SQLalchemy
class Base(DeclarativeBase): 
    pass

db_account = SQLAlchemy(model_class=Base)

app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///session.db'
db_account.init_app(app)

class Account(UserMixin, db_account.Model): 
    id = db_account.Column(db_account.String(255), primary_key=True, unique=True, nullable=False)
    Password = db_account.Column(db_account.String(255), nullable=False)
    Email = db_account.Column(db_account.String(255), nullable=False, unique=True)

    def get_id(self):
        return str(self.id)

with app.app_context():
    db_account.create_all()

#flask-login 
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.init_app(app)

#creation de la session propre à l'user 
def create_user_session():
    return {
        'key': secrets.token_urlsafe(24),
        'session_creation_time': datetime.now(tz=timezone.utc),
    }

#gestion de la session actuel de l'user 
def is_user_session_expired(user_session):

    if not user_session:
        return False

    #cette ligne retourne l'heure à laquelle la session doit expirée 
    expiration_time = user_session['session_creation_time'] + timedelta(hours=1)
    if datetime.now(tz=timezone.utc) > expiration_time:
        return False
    else:
        return True


@login_manager.user_loader
def load_user(user_id): 
    return Account.query.get((user_id))


@app.route("/login", methods=['GET', 'POST']) 
def login(): 
    session.clear()
    if request.method == 'POST': 
        if not request.form.get("username"): 
            return render_template("login.html", attention = "Vous devez transmettre un identifiant")
        
        if not request.form.get("password"): 
            return render_template("login.html", attention = "Vous devez transmettre un mot de passe")
        
        user_informations = Account.query.filter_by(id = request.form.get("username")).first()

        if user_informations: 
            if bcrypt.check_password_hash(user_informations.Password, request.form.get("password")): 
                session['secret_key'] = create_user_session()
                login_user(user_informations)

                return render_template('accueil.html', secret_key=session['secret_key'])
            else: 
                return render_template("login.html", attention = "identifiant ou mot de passe invalide")
        else: 
            return render_template("login.html", attention = "identifiant ou mot de passe invalide")

    else : 
        return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register(): 
    if request.method == 'POST': 

        # Vérifier les données saisies par l'user 
        if not request.form.get("username"): 
            return render_template("register.html", attention = "Vous devez transmettre un identifiant")
        if not request.form.get("Email"): 
            return render_template("register.html", attention = "Vous devez transmettre une adresse E-mail")
        if not request.form.get("password"): 
            return render_template("register.html", attention = "Vous devez transmettre un mot de passe")
        if not request.form.get("password2"): 
            return render_template("register.html", attention = "Vous devez confirmer votre mot de passe")
        MP = test_password(request.form.get("password"))
        if MP == False : 
            return render_template("register.html", attention = "Le mot de passe doit contenir 8 caractères et minimum 1 MAJ, 1 MIN et 1 chiffre")
        if request.form.get("password") != request.form.get("password2"):
            return render_template("register.html", attention = "Erreur dans la confirmation du mot de passe")
        
        user_informations = Account.query.filter_by(id = request.form.get("username")).first()
        if user_informations: 
            return render_template("register.html", attention = "Ce nom d'utilisateur existe déjà")

        #Si toutes les données sont valides on les enregistres 
        identifiant = request.form.get('username')
        email = request.form.get('Email')
        password = bcrypt.generate_password_hash(request.form.get('password'))
        account = Account(id = identifiant, Password = password, Email = email)
        db_account.session.add(account)
        db_account.session.commit()

        return render_template('login.html')

    else: 
        return render_template("register.html")
    
@app.route("/logout")
@login_required
def logout():
    secret_key = session.get('secret_key')
    #rechercher les fichiers commencant par la secret_key et les supprimer
    remove_file(uploads_dir, secret_key)

    return redirect(url_for('login'))

@app.route("/")
@login_required
def accueil():
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == True :
        return render_template("accueil.html", secret_key=session['secret_key'])
    else:
        # Redirigez ou gérez l'absence de secret_key
        return redirect(url_for('logout'))
    


@app.route("/fichier", methods=["GET", "POST"])
@login_required
def fichier(): 
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    if request.method == "POST":
        if "fichiercsv" in request.files:
            fichier_upload = request.files["fichiercsv"]

            if fichier_upload.filename != "":
                nom_fichier = f"{secret_key['key']}.csv"

                fichier_upload.save(os.path.join(uploads_dir, nom_fichier))

                if fichier_upload.filename.lower().endswith(".csv"):
                    chemin_fichier = os.path.join(uploads_dir, nom_fichier)
                    #récupere la liste donner par l'user 
                    fichier = pd.read_csv(chemin_fichier, delimiter=';', encoding='latin-1')
                    #transforme la liste de l'user en une liste détaillé  
                    try: 
                        new_list = transform_file(fichier)
                        new_list.to_csv(chemin_fichier, sep=';', index=False)
                    except Exception as e: 
                        return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des copropriétaires, veillez à transmettre le document d'origine d'ICS",erreur='', secret_key=session['secret_key'])
            

                    # on liste la ou les copropriétés présente dans notre nouvelle liste et le nombre de copro qu'on renvoie au second form 
                    liste_coproprietes = names_coproprietes(chemin_fichier)
                    nombre_coproprietes = len(liste_coproprietes)
                    return render_template("listecopro2.html", liste_coproprietes = liste_coproprietes, nombre_coproprietes = nombre_coproprietes, user_secret_key = secret_key, secret_key=session['secret_key'] )
                    

                else:
                    # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                    os.remove(chemin_fichier)
                    return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='', secret_key=session['secret_key'])
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné.", erreur='', secret_key=session['secret_key'])
        else: 
            return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='', secret_key=session['secret_key'])
    else: 
        return render_template("listecopro.html", secret_key=session['secret_key'])

#affichage du 2eme form avant la création de liste_copropriétaires.csv
@app.route("/fichier/RP", methods=["GET", "POST"])
@login_required
def form(): 
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    if request.method == "POST":
        if request.form.get("OuiNon_RP")== "oui":
            # On refait la liste des différentes copro pour connaitre le nombre de retour
            new_list = os.path.join(uploads_dir, f"{secret_key['key']}.csv")

            try: 
                liste_coproprietes = names_coproprietes(new_list)
            except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des immeubles, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])
            
            nombre_coproprietes = len(liste_coproprietes)

            # on liste copro par copro les adresses recu 
            for copropriete in range(nombre_coproprietes): 
                if request.form.get(f"adresses_{liste_coproprietes[copropriete]}"):
                    nom_immeuble = liste_coproprietes[copropriete]
                    adresse_residence = request.form.get(f"adresses_{liste_coproprietes[copropriete]}") 
                    
                    try :
                        df = residence_principale(new_list, adresse_residence, nom_immeuble)
                        df.to_csv(new_list, sep=';', index=False)
                    except Exception as e: 
                        return render_template("erreur.html", attention = "une erreur s'est produite lors de la recherche de résidence principale, veillez à transmettre le document d'origine d'ICS et les adresses des copropriétés sous cette form 'adresse, code postal ville'", erreur="", secret_key=session['secret_key'])
                    
                else : 
                    continue

            # fonction de renvoie de ma nouvelle liste
            return render_template("listecopro3.html", secret_key=session['secret_key'])
        else: 
            new_list = os.path.join(uploads_dir, f"{secret_key['key']}.csv")
            liste_csv = pd.read_csv(new_list, delimiter=';', encoding='latin-1')
            if 'RP' in liste_csv.columns : 
                del liste_csv['RP']
            liste_csv.to_csv(new_list, sep=';', index=False)
            return render_template("listecopro3.html", secret_key=session['secret_key'])
    else: 
        nom_fichier = f"{secret_key['key']}.csv"
        if os.path.isfile(nom_fichier): 
            liste_csv = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
            #on rajoute la colonne RP si on ne l'a plus 
            liste_csv.insert(2, 'RP', 'Non', allow_duplicates=False)
            liste_csv.to_csv(nom_fichier, sep=';', index=False)
            liste_coproprietes = names_coproprietes(nom_fichier)
            nombre_coproprietes = len(liste_coproprietes)
            return render_template("listecopro2.html",liste_coproprietes = liste_coproprietes , nombre_coproprietes = nombre_coproprietes, secret_key=session['secret_key'])
        else: 
            return render_template("listecopro.html", secret_key=session['secret_key'])

#page pour ajouter les numéro de lot 
@app.route("/fichier/lot", methods=["GET", "POST"])
@login_required
def form2():
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    
    if request.method == "POST":
        if request.form.get("OuiNon_lot") == "oui": 
            if "lot_csv" in request.files:
                fichier_upload = request.files["lot_csv"]
                if fichier_upload.filename != "":
                    nom_fichier = f"{secret_key['key']}lots.csv"

                    fichier_upload.save(os.path.join(uploads_dir, nom_fichier))

                    if fichier_upload.filename.lower().endswith(".csv"):
                        nom_fichier = os.path.join(uploads_dir, nom_fichier)
                        #récupere la liste donner par l'user 
                        liste_lot = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                        
                        #récupère les noms/prénoms en enlevant le ()
                        try :  
                            fichier_lot = tri_liste_lot(liste_lot)
                            fichier_lot.to_csv(nom_fichier, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des lots, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])

                        #pour chaque nom de copropritaire ajouter une colonne avec lot de l'appartement
                        new_list = os.path.join(uploads_dir, f"{secret_key['key']}.csv")
                        try :
                            df = add_lot(nom_fichier, new_list)
                            df.to_csv(new_list, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la transmission des lots à votre liste copropriétaire, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])

                        return render_template("downloads_liste_coproprietaires.html", secret_key=session['secret_key'])
                        

                    else:
                        # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                        os.remove(nom_fichier)
                        return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='', secret_key=session['secret_key'])
                else:
                    return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné", erreur='', secret_key=session['secret_key'])
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='', secret_key=session['secret_key'])
        else:
            new_list = os.path.join(uploads_dir, f"{secret_key['key']}.csv")
            liste_csv = pd.read_csv(new_list, delimiter=';', encoding='latin-1')
            del liste_csv['lot_logement']
            del liste_csv['n_lot/n_plan/localisation(bat,esc,etg,pt)']
            del liste_csv['lot_professionnel']
            del liste_csv['lot_autre']
            liste_csv.to_csv(new_list, sep=';', index=False)
            return render_template("downloads_liste_coproprietaires.html", secret_key=session['secret_key'])
    else: 
        return render_template("listecopro3.html", secret_key=session['secret_key'])
    
#page d'indication et de bouton de téléchargement de liste_copropriétaires.csv
@app.route('/liste_coproprietaires_downloads')
@login_required
def page_de_telechargement():
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    
    fichier = os.path.join(uploads_dir, f"{secret_key['key']}.csv")
    return render_template("downloads_liste_coproprietaires.html", fichier = fichier, secret_key=session['secret_key'])

# fonction de renvoie de ma nouvelle liste
@app.route('/downloads')
@login_required
def telechargement(): 
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    fichier = os.path.join(uploads_dir, f"{secret_key['key']}.csv")
    return send_file(fichier, 
        as_attachment=True,
        download_name='liste_coproprietaires.csv',
        mimetype='text/csv')


@app.route('/MAJliste', methods=["GET", "POST"])
@login_required
def recuperer_newliste():
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    if request.method == "POST":
        fichiers_user = ["votre_liste", "liste_ics"]
        name_fichier = [f"{secret_key['key']}liste_user.csv", f"{secret_key['key']}liste_ics.csv"]
        for name in range(len(fichiers_user)): 
            if fichiers_user[name] in request.files: 
                fichier = request.files[fichiers_user[name]]

                if fichier.filename != "": 
                    fichier.save(os.path.join(uploads_dir, name_fichier[name]))

                    if fichier.filename.lower().endswith(".csv"):
                        continue
                    else:
                        fichier = os.path.join(uploads_dir, name_fichier[name])
                        os.remove(fichier)
                        return render_template("erreur.html", attention = f"Le fichier {fichiers_user[name]} n'est pas un fichier CSV.", erreur='', secret_key=session['secret_key'])
                else: 
                     return render_template("erreur.html", attention = f"Aucun fichier n'a été sélectionné pour '{fichiers_user[name]}'", erreur='', secret_key=session['secret_key'])
            else: 
                return render_template("erreur.html", attention = f"Aucun fichier n'a été téléchargé concernant {fichiers_user[name]}'", erreur='', secret_key=session['secret_key'])
        
        # on met en page comme à la creation le fichier ICS 
        try:
            chemin_ics = os.path.join(uploads_dir, f"{secret_key['key']}liste_ics.csv")
            fichier = pd.read_csv(chemin_ics, delimiter=';', encoding='latin-1')
            df = transform_file(fichier)
            df = df.drop('RP', axis=1)
            #au lieu de listecopropriétaire.csv c'est toujours liste_ics.csv
            df.to_csv(chemin_ics, sep=';', index=False)
        except Exception as e : 
            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des copropriétaires, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])
        

        return render_template("compare_list1.html", secret_key=session['secret_key'])
        
    else:
        return render_template("comparer_liste.html", secret_key=session['secret_key']) 
    
     
@app.route('/MAJliste/lot', methods=["GET", "POST"])
@login_required
def addlot():
    # Générer une clé secrète unique pour cet utilisateur
    secret_key = session.get('secret_key')
    if is_user_session_expired(secret_key) == False: 
        return redirect(url_for('logout'))
    if request.method == "POST":
        if request.form.get("OuiNon_lot") == "oui": 
            if "lot_csv" in request.files:
                fichier_upload = request.files["lot_csv"]
                if fichier_upload.filename != "":
                    nom_fichier = f'{secret_key["key"]}liste_lots.csv'

                    fichier_upload.save(os.path.join(uploads_dir, nom_fichier))

                    if fichier_upload.filename.lower().endswith(".csv"):
                        nom_fichier = os.path.join(uploads_dir, nom_fichier)
                        #récupere la liste donner par l'user 
                        liste_lot = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                        
                        #récupère les noms/prénoms en enlevant le ()
                        try :  
                            df = tri_liste_lot(liste_lot)
                            df.to_csv(nom_fichier, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des lots, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])

                        #pour chaque nom de copropritaire ajouter une colonne avec lot de l'appartement
                        new_list=os.path.join(uploads_dir, f'{secret_key["key"]}liste_ics.csv')
                        try :
                            df = add_lot(nom_fichier, new_list)
                            df.to_csv(new_list, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la transmission des lots à votre liste copropriétaire, veillez à transmettre le document d'origine d'ICS", erreur="", secret_key=session['secret_key'])
                
                    else:
                        # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                        nom_fichier = os.path.join(uploads_dir, nom_fichier)
                        os.remove(nom_fichier)
                        return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='', secret_key=session['secret_key'])
                else:
                    return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné", erreur='', secret_key=session['secret_key'])
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='', secret_key=session['secret_key'])
        else:
            fichier_ics = os.path.join(uploads_dir, f'{secret_key["key"]}liste_ics.csv')
            liste_csv = pd.read_csv(fichier_ics, delimiter=';', encoding='latin-1')
            del liste_csv['lot_logement']
            del liste_csv['n_lot/n_plan/localisation(bat,esc,etg,pt)']
            del liste_csv['lot_professionnel']
            del liste_csv['lot_autre']
            liste_csv.to_csv(fichier_ics, sep=';', index=False)
        

        # on compare ensuite liste_ics.csv et liste_user.csv et renvoie la nouvelle liste vers liste_copropriétaires
        try :
            fichier_ics = os.path.join(uploads_dir, f'{secret_key["key"]}liste_ics.csv')
            fichier_user = os.path.join(uploads_dir, f"{secret_key['key']}liste_user.csv")
            liste_user = compare_list(fichier_ics, fichier_user)
        except Exception as e:
            return render_template("erreur.html", attention = "une erreur s'est produite lors de la mise à jour, veillez à transmettre le document d'origine d'ICS et que vous ayez bien conservé les colonnes nécessaires à la vérification (code_copropriete et code_coproprietaire)", erreur="", secret_key=session['secret_key'])

    
        #on  verifie le retour de compare_list 
        if isinstance(liste_user, pd.DataFrame):
            fichier =  os.path.join(uploads_dir, f"{secret_key['key']}.csv")
            liste_user.to_csv(fichier, sep=';', index=False)
            return render_template("downloads_liste_coproprietaires.html", secret_key=session['secret_key'])
        elif liste_user == 'code_coproprietaire': 
            return render_template("erreur.html", attention = "la colonne 'code_coproprietaire' n'est pas présente dans votre liste impossible de mettre à jour le fichier", secret_key=session['secret_key'])
        elif liste_user == 'code_copropriete': 
            return render_template("erreur.html", attention = "la colonne 'code_copropriete' n'est pas présente dans votre liste impossible de mettre à jour le fichier", secret_key=session['secret_key'])

    else:
        return render_template("compare_list1.html", secret_key=session['secret_key']) 


app.config['ENV'] = 'production'

if __name__ == "__main__":
    app.run(debug=False)
