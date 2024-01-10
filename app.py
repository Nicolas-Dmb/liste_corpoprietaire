#flask run --host=0.0.0.0

import os
from flask import Flask, flash, render_template, request, send_file, url_for, redirect, session
import pandas as pd
import atexit 
import shutil
from test import transform_file
from excel import names_coproprietes, residence_principale
from lots import tri_liste_lot, add_lot
from compare import compare_list

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

app.secret_key = os.urandom(24)

@app.route("/")
def accueil():
    return render_template("accueil.html")


@app.route("/fichier", methods=["GET", "POST"])
def fichier(): 
    if request.method == "POST":
        if "fichiercsv" in request.files:
            fichier_upload = request.files["fichiercsv"]

            if fichier_upload.filename != "":
                nom_fichier = f"/tmp/{app.secret_key}.csv"

                fichier_upload.save(nom_fichier)

                if fichier_upload.filename.lower().endswith(".csv"):
                    
                    #récupere la liste donner par l'user 
                    fichier = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                    #transforme la liste de l'user en une liste détaillé  
                    try: 
                        new_list = transform_file(fichier)
                        new_list.to_csv(nom_fichier, sep=';', index=False)
                    except Exception as e: 
                        return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des copropriétaires, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")
            

                    # on liste la ou les copropriétés présente dans notre nouvelle liste et le nombre de copro qu'on renvoie au second form 
                    liste_coproprietes = names_coproprietes(nom_fichier)
                    nombre_coproprietes = len(liste_coproprietes)
                    return render_template("listecopro2.html", liste_coproprietes = liste_coproprietes, nombre_coproprietes = nombre_coproprietes )
                    

                else:
                    # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                    os.remove(nom_fichier)
                    return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='')
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné.", erreur='')
        else: 
            return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='')
    else: 
        return render_template("listecopro.html")

#affichage du 2eme form avant la création de liste_copropriétaires.csv
@app.route("/fichier/RP", methods=["GET", "POST"])
def form(): 
    if request.method == "POST":
        if request.form.get("OuiNon_RP")== "oui":
            # On refait la liste des différentes copro pour connaitre le nombre de retour
            new_list = f"/tmp/{app.secret_key}.csv"

            try: 
                liste_coproprietes = names_coproprietes(new_list)
            except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des immeubles, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")
            
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
                        return render_template("erreur.html", attention = "une erreur s'est produite lors de la recherche de résidence principale, veillez à transmettre le document d'origine d'ICS et les adresses des copropriétés sous cette form 'adresse, code postal ville'", erreur=f"erreur retournée : {str(e)}")
                    
                else : 
                    continue

            # fonction de renvoie de ma nouvelle liste
            return redirect("/fichier/lot")
        else: 
            new_list = f"/tmp/{app.secret_key}.csv"
            liste_csv = pd.read_csv(new_list, delimiter=';', encoding='latin-1')
            if 'RP' in liste_csv.columns : 
                del liste_csv['RP']
            liste_csv.to_csv(new_list, sep=';', index=False)
            return redirect("/fichier/lot")
    else: 
        nom_fichier = f"/tmp/{app.secret_key}.csv"
        if os.path.isfile(nom_fichier): 
            liste_csv = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
            #on rajoute la colonne RP si on ne l'a plus 
            liste_csv.insert(2, 'RP', 'Non', allow_duplicates=False)
            liste_csv.to_csv(nom_fichier, sep=';', index=False)
            liste_coproprietes = names_coproprietes(nom_fichier)
            nombre_coproprietes = len(liste_coproprietes)
            return render_template("listecopro2.html",liste_coproprietes = liste_coproprietes , nombre_coproprietes = nombre_coproprietes)
        else: 
            return render_template("listecopro.html")

#page pour ajouter les numéro de lot 
@app.route("/fichier/lot", methods=["GET", "POST"])
def form2():
    if request.method == "POST":
        if request.form.get("OuiNon_lot") == "oui": 
            if "lot_csv" in request.files:
                fichier_upload = request.files["lot_csv"]
                if fichier_upload.filename != "":
                    nom_fichier = f"/tmp/{app.secret_key}lots.csv"

                    fichier_upload.save(nom_fichier)

                    if fichier_upload.filename.lower().endswith(".csv"):
                        
                        #récupere la liste donner par l'user 
                        liste_lot = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                        
                        #récupère les noms/prénoms en enlevant le ()
                        try :  
                            fichier_lot = tri_liste_lot(liste_lot)
                            fichier_lot.to_csv(nom_fichier, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des lots, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")

                        #pour chaque nom de copropritaire ajouter une colonne avec lot de l'appartement
                        new_list=f"/tmp/{app.secret_key}.csv"
                        try :
                            df = add_lot(nom_fichier, new_list)
                            df.to_csv(new_list, sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la transmission des lots à votre liste copropriétaire, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")

                        return redirect("/liste_coproprietaires_downloads")
                        

                    else:
                        # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                        os.remove(nom_fichier)
                        return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='')
                else:
                    return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné", erreur='')
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='')
        else:
            liste_csv = pd.read_csv(f"/tmp/{app.secret_key}.csv", delimiter=';', encoding='latin-1')
            del liste_csv['lot_logement']
            del liste_csv['n_lot/n_plan/localisation(bat,esc,etg,pt)']
            del liste_csv['lot_professionnel']
            del liste_csv['lot_autre']
            liste_csv.to_csv(f"/tmp/{app.secret_key}.csv", sep=';', index=False)
            return redirect("/liste_coproprietaires_downloads")
    else: 
        return render_template("listecopro3.html")
    
#page d'indication et de bouton de téléchargement de liste_copropriétaires.csv
@app.route('/liste_coproprietaires_downloads')
def page_de_telechargement():
    fichier = f"/tmp/{app.secret_key}.csv"
    return render_template("downloads_liste_coproprietaires.html", fichier = fichier)

# fonction de renvoie de ma nouvelle liste
@app.route('/downloads')
def telechargement(): 
        return send_file(f"/tmp/{app.secret_key}.csv", 
            as_attachment=True,
            download_name='liste_coproprietaires.csv',
            mimetype='text/csv')


@app.route('/MAJliste', methods=["GET", "POST"])
def recuperer_newliste(): 
    if request.method == "POST":
        fichiers_user = ["votre_liste", "liste_ics"]
        name_fichier = [f"/tmp/{app.secret_key}liste_user.csv", f"/tmp/{app.secret_key}liste_ics.csv"]
        for name in range(len(fichiers_user)): 
            if fichiers_user[name] in request.files: 
                fichier = request.files[fichiers_user[name]]

                if fichier.filename != "": 
                    fichier.save(name_fichier[name])

                    if fichier.filename.lower().endswith(".csv"):
                        continue
                    else:
                        os.remove(name_fichier[name])
                        return render_template("erreur.html", attention = f"Le fichier {fichiers_user[name]} n'est pas un fichier CSV.", erreur='')
                else: 
                     return render_template("erreur.html", attention = f"Aucun fichier n'a été sélectionné pour '{fichiers_user[name]}'", erreur='')
            else: 
                return render_template("erreur.html", attention = f"Aucun fichier n'a été téléchargé concernant {fichiers_user[name]}'", erreur='')
        
        # on met en page comme à la creation le fichier ICS 
        try: 
            fichier = pd.read_csv(f"/tmp/{app.secret_key}liste_ics.csv", delimiter=';', encoding='latin-1')
            df = transform_file(fichier)
            df = df.drop('RP', axis=1)
            #au lieu de listecopropriétaire.csv c'est toujours liste_ics.csv
            df.to_csv(f"/tmp/{app.secret_key}liste_ics.csv", sep=';', index=False)
        except Exception as e : 
            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des copropriétaires, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")
        

        return render_template("compare_list1.html")
        
    else:
        return render_template("comparer_liste.html") 
    
     
@app.route('/MAJliste/lot', methods=["GET", "POST"])
def addlot(): 
    if request.method == "POST":
        if request.form.get("OuiNon_lot") == "oui": 
            if "lot_csv" in request.files:
                fichier_upload = request.files["lot_csv"]
                if fichier_upload.filename != "":
                    nom_fichier = f'/tmp/{app.secret_key}liste_lots.csv'

                    fichier_upload.save(nom_fichier)

                    if fichier_upload.filename.lower().endswith(".csv"):
                        
                        #récupere la liste donner par l'user 
                        liste_lot = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                        
                        #récupère les noms/prénoms en enlevant le ()
                        try :  
                            df = tri_liste_lot(liste_lot)
                            df.to_csv(f"/tmp/{app.secret_key}liste_lots.csv", sep=';', index=False)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la récupération des lots, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")

                        #pour chaque nom de copropritaire ajouter une colonne avec lot de l'appartement
                        new_list=f'/tmp/{app.secret_key}liste_ics.csv'
                        try :
                            new_list = add_lot(f"/tmp/{app.secret_key}liste_lots.csv", new_list)
                        except Exception as e: 
                            return render_template("erreur.html", attention = "une erreur s'est produite lors de la transmission des lots à votre liste copropriétaire, veillez à transmettre le document d'origine d'ICS", erreur=f"erreur retournée : {str(e)}")

                        return redirect("/MAJliste/2")
                        

                    else:
                        # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                        os.remove(nom_fichier)
                        return render_template("erreur.html", attention = "Le fichier téléchargé n'est pas un fichier CSV.", erreur='')
                else:
                    return render_template("erreur.html", attention = "Aucun fichier n'a été sélectionné", erreur='')
            else:
                return render_template("erreur.html", attention = "Aucun fichier n'a été téléchargé dans la requête.", erreur='')
        else:
            liste_csv = pd.read_csv(f'/tmp/{app.secret_key}liste_ics.csv', delimiter=';', encoding='latin-1')
            del liste_csv['lot_logement']
            del liste_csv['n_lot/n_plan/localisation(bat,esc,etg,pt)']
            del liste_csv['lot_professionnel']
            del liste_csv['lot_autre']
            liste_csv.to_csv(f'/tmp/{app.secret_key}liste_ics.csv', sep=';', index=False)
            return redirect("/MAJliste/2")
    else:
        return render_template("comparer_liste.html") 

@app.route('/MAJliste/2')
def MAJliste(): 
    #on compare liste_ics.csv et liste_user.csv et sa renvoie la nouvelle liste vers liste_copropriétaires
    try : 
        liste_user = compare_list(f'/tmp/{app.secret_key}liste_ics.csv', f"/tmp/{app.secret_key}liste_user.csv")
    except Exception as e:
        return render_template("erreur.html", attention = "une erreur s'est produite lors de la mise à jour, veillez à transmettre le document d'origine d'ICS et que vous ayez bien conservé les colonnes nécessaires à la vérification (code_copropriete et code_coproprietaire)", erreur=f"erreur retournée : {str(e)}")

    
    #on  verifie le retour de compare_list 
    if isinstance(liste_user, pd.DataFrame):
        liste_user.to_csv(f"/tmp/{app.secret_key}.csv", sep=';', index=False)
        return redirect("/liste_coproprietaires_downloads")
    elif liste_user == 'code_coproprietaire': 
        return render_template("erreur.html", attention = "la colonne 'code_coproprietaire' n'est pas présente dans votre liste impossible de mettre à jour le fichier")
    elif liste_user == 'code_copropriete': 
        return render_template("erreur.html", attention = "la colonne 'code_copropriete' n'est pas présente dans votre liste impossible de mettre à jour le fichier")


app.config['ENV'] = 'production'

if __name__ == "__main__":
    app.run(debug=False)
