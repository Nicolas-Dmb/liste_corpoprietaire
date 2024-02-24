import os 
import datetime
from datetime import timezone
from app import app

uploads_dir = os.path.join(app.instance_path, 'files')

# Durée maximum du fichier 
Max_file_age = 1 

def delete_old_files(directory): 
    now = datetime.datetime.now()
    for filename in os.listdir(directory): 
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path): 
            #obtenir l'heure de création du fichier 
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            #calculer la différence entre l'heure actuelle et l'heure de creation 
            age = now - creation_time
            #si le fichier est plus ancien que 1 heure, on supprime 
            if age.total_seconds() / 3600 > Max_file_age : 
                os.remove(file_path)


delete_old_files(uploads_dir)