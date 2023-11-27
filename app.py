#flask run --host=0.0.0.0

import os
from flask import Flask, flash, render_template, request, send_file, url_for
import pandas as pd
from test import transform_file
from excel import names_coproprietes, residence_principale

app=Flask(__name__)

#ma liste créer via le fichier de l'user et l'ajoute de colonne 
new_list=''

@app.route("/")
def homepage():
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
                    global new_list 
                    new_list = transform_file(fichier)

                     
                    # on liste la ou les copropriétés présente dans notre nouvelle liste et le nombre de copro qu'on renvoie au second form 
                    liste_coproprietes = names_coproprietes(new_list)
                    nombre_coproprietes = len(liste_coproprietes)
                    return render_template("listecopro2.html", liste_coproprietes = liste_coproprietes, nombre_coproprietes = nombre_coproprietes)
                    

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


@app.route("/fichier/RP", methods=["GET", "POST"])
def form(): 
    if request.method == "POST":
        # On refait la liste des différentes copro pour connaitre le nombre de retour
        liste_coproprietes = names_coproprietes(new_list)
        nombre_coproprietes = len(liste_coproprietes)

        # on liste copro par copro les adresses recu 
        for copropriete in range(nombre_coproprietes): 
            if request.form.get("adresses_{liste_coproprietes[copropriete]}"):
                nom_immeuble = liste_coproprietes[copropriete]
                adresse_residence = request.form.get("adresses_{liste_coproprietes[copropriete]}") 

                new_list = residence_principale(new_list, adresse_residence, nom_immeuble)
            else : 
                continue
        
        # fonction de renvoie de ma nouvelle liste
        return send_file(
            new_list, 
            as_attachment=True,
            download_name='liste_coproprietaires.csv',
            mimetype='text/csv'
            )

    else: 
        return render_template("listecopro2.html")




if __name__ == "__main__":
    app.run(debug=True)
