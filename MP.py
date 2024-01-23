import re

def test_password(password):
    chiffre = bool(re.search(r'\d', password))
    majuscule = bool(re.search(r'[A-Z]', password))
    minuscule = bool(re.search(r'[a-z]', password))
    if chiffre == True and majuscule == True and minuscule == True : 
        return True 
    else : 
        return False 