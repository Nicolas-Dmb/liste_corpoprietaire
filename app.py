#flask run --host=0.0.0.0

import os
from flask import Flask, flash, render_template, request, send_file, url_for
import pandas as pd
from test import transform_file

app=Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/fichier", methods=["GET", "POST"])
def fichier(): 
    if request.method == "POST":
        if "fichiercsv" in request.files:
            fichier_upload = request.files["fichiercsv"]

            if fichier_upload.filename != "":
                nom_fichier = 'liste_coproprietaires.csv'

                fichier_upload.save(nom_fichier)

                if nom_fichier.lower().endswith(".csv"):

                    fichier = pd.read_csv(nom_fichier, delimiter=';', encoding='latin-1')
                    nom_fichier = transform_file(fichier)

                    return send_file(
                        nom_fichier, 
                        as_attachment=True,
                        download_name='liste_coproprietaires.csv',
                        mimetype='text/csv'
                    )

                else:
                    # Si ce n'est pas un fichier CSV, vous pouvez supprimer le fichier et renvoyer un message d'erreur
                    os.remove(nom_fichier)
                    return "Le fichier téléchargé n'est pas un fichier CSV."
            else:
                return "Aucun fichier n'a été sélectionné."
        else: 
            return "Aucun fichier n'a été téléchargé dans la requête."
    else: 
        return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True)
