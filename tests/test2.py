import pandas as pd

def names_coproprietes(liste_csv):
    names_coproprietes=[]
    for row in range(len(liste_csv)):
        if row == 0:
            names_coproprietes.append(liste_csv['copropriete'][row])
        else:
            name_copropriete = 0
            while name_copropriete < len(names_coproprietes) and names_coproprietes[name_copropriete] != liste_csv['copropriete'][row]:
                name_copropriete +=1
            if name_copropriete == len(names_coproprietes): 
                names_coproprietes.append(liste_csv['copropriete'][row])
    return names_coproprietes                            
                
# on trie les adresses recu de la résidence on en fait des mots clés et on verifie _ on recoi les adresses une à une
def residence_principale(liste_csv, adresse_copropriete, nom_immeuble):
    # on fait des mots clés avec l'adresse de l'immeuble
    key_word = [] #mots clés de l'adresse de l'immeuble (sans CP ou numéro)
    adresse_copropriete = adresse_copropriete + ' ' #pour controler le dernier mot 
    CP = ''
    not_key_word=[ 'rue', 'du', 'le', 'route', 'de', 'la', 'allee', 'des', 'avenue', 'av', 'bd', 'des', 'apt', 'square', 'les', 'residence', 'sur', 'bld', 'boulevard', 'av.', 'quai', 'chemin', 'cours', 'ter', 'res', 'au', 'aux', 'l', 'parc', 'impasse', 'imp', 'd', 'place', 'pl']
    word_inprogress =''
    typeOfstring = ''
    lenOfword = 0
    # On pourrait amelliorer cette partie en faisant un .split sur l'adresse puis en vérifiant les mots via not key word et la suite de chiffre pour CP attention toutefois au espace 35 400 
    for char in range(len(adresse_copropriete)): 
        if 47 < ord(adresse_copropriete[char]) < 58: 
            word_inprogress += str(adresse_copropriete[char])
            typeOfstring = 'int'
            lenOfword += 1
        elif 96 < ord(adresse_copropriete[char].lower()) < 123 or typeOfstring == 'str' and adresse_copropriete[char] == '-': 
            word_inprogress += str(adresse_copropriete[char].lower())
            typeOfstring = 'str'
            lenOfword += 1
        elif adresse_copropriete[char] == ' ':
            next_char ='I'
            if char+1 < len(adresse_copropriete): 
                next_char = adresse_copropriete[char+1]
                if next_char==' ' and char+2 < len(adresse_copropriete): 
                    next_char = adresse_copropriete[char+2]
            if typeOfstring == 'int' and lenOfword == 5:
                CP = word_inprogress
                typeOfstring=''
                lenOfword = 0
                word_inprogress=''
            elif typeOfstring == 'int' and lenOfword == 2 and 47 < ord(next_char) < 58 :
                continue
            elif typeOfstring == 'str': 
                for word in range(len(not_key_word)): 
                    if not_key_word[word] == word_inprogress: 
                        word_inprogress=''
                        typeOfstring=''
                        lenOfword = 0
                        break
                if word_inprogress != '': 
                    key_word.append(word_inprogress)
                    word_inprogress=''
                    typeOfstring=''
                    lenOfword = 0
            else: 
                typeOfstring=''
                lenOfword = 0
                word_inprogress=''
            
        else: 
            continue

                
    # on liste les copropriétaires dans liste_csv on vérifie ceux de l'immeuble puis ceux de la ville de l'immeuble puis l'adresse 
    for row in range(len(liste_csv)) :
        if liste_csv['copropriete'][row] == nom_immeuble: 
            ville_coproprietaire = liste_csv['ville'][row]
            CP_coproprietaire= ''
            for char in range(len(ville_coproprietaire)): 
                if 47 < ord(ville_coproprietaire[char]) < 58 : 
                    CP_coproprietaire += ville_coproprietaire[char]
                elif ville_coproprietaire[char] == ' ': 
                    continue
                else: 
                    break
            if CP_coproprietaire == CP: 
                adresse_coproprietaire = liste_csv['adresse'][row]
                list_adresse_coproprietaire = adresse_coproprietaire.split()
                for word_copropriete in range(len(key_word)): 
                    for word_coproprietaire in range(len(list_adresse_coproprietaire)):
                        word_coproprietaire_verif = list_adresse_coproprietaire[word_coproprietaire]
                        key_word_copropriete = key_word[word_copropriete]
                        if word_coproprietaire_verif.lower() == key_word_copropriete.lower(): 
                            liste_csv['RP'][row] = "Oui"
                            break # on pourrait amelliorer la rapidité pour qu'il se coupe ici dès qu'il y a trouvé un mot similaire. car il coupe que la deuxième boucle 
        else: 
            continue
    
    # a modifier pour que tout se mette sur liste_coproprietaires 
    df = pd.DataFrame(liste_csv)
    df.to_csv('liste_coproprietaires_RP.csv', sep=';', index=False)
    return 'liste_coproprietaires_RP.csv'



fichier = pd.read_csv('liste_coproprietaires.csv', delimiter=';', encoding='latin-1')
list_coproprietes = names_coproprietes(fichier)
list_adresses_copropriete = ['2 Avenue Aristide Briand 35 400 St Malo 1 Avenue Anita Conti, 35 400 Saint-Malo''1 Rue de la croix des marais, 35 400 Saint-Malo']

for adresse in range(len(list_adresses_copropriete)): 
    new_list = residence_principale(fichier, list_adresses_copropriete[adresse], list_coproprietes[adresse])

