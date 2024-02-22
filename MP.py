import re
import os

def test_password(password):
    chiffre = bool(re.search(r'\d', password))
    majuscule = bool(re.search(r'[A-Z]', password))
    minuscule = bool(re.search(r'[a-z]', password))
    if chiffre == True and majuscule == True and minuscule == True : 
        return True 
    else : 
        return False 
    
def remove_file(uploads_dir, secret_key):
    for dirpath, dirname, files in os.walk(uploads_dir):
        for file in files : 
            print(file)
            print(secret_key['key'])
            if re.search(f"{secret_key['key']}", file):
                chemin_fichier = f"{dirpath}/" + f"{file}"
                os.remove(chemin_fichier)
    return