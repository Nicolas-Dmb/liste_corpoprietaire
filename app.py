#flask run --host=0.0.0.0

import os
from flask import Flask, flash, render_template, request, send_file, url_for, redirect
import pandas as pd
import threading
import time
from test import transform_file
from excel import names_coproprietes, residence_principale
from lots import tri_liste_lot, add_lot

app=Flask(__name__)


@app.route("/")
def homepage():
    if os.path.exists("liste_coproprietaires.csv"):
        os.remove("liste_coproprietaires.csv")
    return render_template("listecopro.html")

@app.route("/fichier", methods=["GET", "POST"])
def fichier(): 
    if request.method == "POST":
        if "fichiercsv" in request.files:
            fichier_upload = request.files["fichiercsv"]

            if fichier_upload.filename != "":
                nom_fichier = 'liste_coproprietaires.csv'

                fichier_upload.save(nom_fichier)

                if nom_fichier.lower().endswith(".csv"):
                    
                    #récupere la liste donner par l'user 
                    fichier = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                    #transforme la liste de l'user en une liste détaillé  
                    new_list = transform_file(fichier)


                    # on liste la ou les copropriétés présente dans notre nouvelle liste et le nombre de copro qu'on renvoie au second form 
                    liste_coproprietes = names_coproprietes(new_list)
                    nombre_coproprietes = len(liste_coproprietes)
                    return render_template("listecopro2.html", liste_coproprietes = liste_coproprietes, nombre_coproprietes = nombre_coproprietes )
                    

                else:
                    # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                    os.remove(nom_fichier)
                    return "Le fichier téléchargé n'est pas un fichier CSV."
            else:
                return "Aucun fichier n'a été sélectionné."
        else: 
            return "Aucun fichier n'a été téléchargé dans la requête."
    else: 
        return render_template("listecopro.html")

#affichage du 2eme form avant la création de liste_copropriétaires.csv
@app.route("/fichier/RP", methods=["GET", "POST"])
def form(): 
    if request.method == "POST":
        if request.form.get("OuiNon_RP")== "oui":
            # On refait la liste des différentes copro pour connaitre le nombre de retour
            new_list = 'liste_coproprietaires.csv'
            liste_coproprietes = names_coproprietes(new_list)
            nombre_coproprietes = len(liste_coproprietes)

            # on liste copro par copro les adresses recu 
            for copropriete in range(nombre_coproprietes): 
                if request.form.get(f"adresses_{liste_coproprietes[copropriete]}"):
                    nom_immeuble = liste_coproprietes[copropriete]
                    adresse_residence = request.form.get(f"adresses_{liste_coproprietes[copropriete]}") 
                    
                    new_list = residence_principale(new_list, adresse_residence, nom_immeuble)
                else : 
                    continue

            # fonction de renvoie de ma nouvelle liste
            return redirect("/fichier/lot")
        else: 
            liste_csv = pd.read_csv('liste_coproprietaires.csv', delimiter=';', encoding='latin-1')
            del liste_csv['RP']
            liste_csv.to_csv('liste_coproprietaires.csv', sep=';', index=False)
            return redirect("/fichier/lot")
    else: 
        return render_template("listecopro2.html")

#page pour ajouter les numéro de lot 
@app.route("/fichier/lot", methods=["GET", "POST"])
def form2():
    if request.method == "POST":
        if request.form.get("OuiNon_lot") == "oui": 
            if "lot_csv" in request.files:
                fichier_upload = request.files["lot_csv"]
                if fichier_upload.filename != "":
                    nom_fichier = 'liste_lots.csv'

                    fichier_upload.save(nom_fichier)

                    if nom_fichier.lower().endswith(".csv"):
                        
                        #récupere la liste donner par l'user 
                        liste_lot = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                        #récupère les noms/prénoms en enlevant le () 
                        fichier_lot = tri_liste_lot(liste_lot)

                        #pour chaque nom de copropritaire ajouter une colonne avec lot de l'appartement
                        new_list='liste_coproprietaires.csv'
                        new_list = add_lot(fichier_lot, new_list)

                        return redirect("/liste_coproprietaires_downloads")
                        

                    else:
                        # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                        os.remove(nom_fichier)
                        return "Le fichier téléchargé n'est pas un fichier CSV."
                else:
                    return "Aucun fichier n'a été sélectionné."
            else: 
                return "Aucun fichier n'a été téléchargé dans la requête."
        else:
            liste_csv = pd.read_csv('liste_coproprietaires.csv', delimiter=';', encoding='latin-1')
            del liste_csv['lot_logement']
            del liste_csv['n_lot/n_plan/localisation(bat,esc,etg,pt)']
            del liste_csv['lot_professionnel']
            del liste_csv['lot_autre']
            liste_csv.to_csv('liste_coproprietaires.csv', sep=';', index=False)
            return redirect("/liste_coproprietaires_downloads")
    else: 
        return render_template("listecopro3.html")
    
#page d'indication et de bouton de téléchargement de liste_copropriétaires.csv
@app.route('/liste_coproprietaires_downloads')
def page_de_telechargement():
    return render_template("downloads_liste_coproprietaires.html")

# fonction de renvoie de ma nouvelle liste
@app.route('/downloads')
def telechargement(): 
        return send_file('liste_coproprietaires.csv', 
            as_attachment=True,
            download_name='liste_coproprietaires.csv',
            mimetype='text/csv')

if __name__ == "__main__":
    app.run(debug=True)
