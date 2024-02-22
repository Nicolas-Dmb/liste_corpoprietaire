import pandas as pd

def names_coproprietes(liste_csv):
    names_coproprietes=[]
    liste = pd.read_csv(liste_csv, delimiter=';', encoding='latin-1', dtype='str')
    liste.columns = ['code_coproprietaire','Nom','civilite','code_copropriete', 'copropriete','adresse','ville','RP','tel1','tel2','tel3', 'mail1','mail2','mail3','informations1','informations2','informations3', 'lot_logement','n_lot/n_plan/localisation(bat,esc,etg,pt)','lot_professionnel','lot_autre']
    for row in range(len(liste)):
        if row == 0:
            names_coproprietes.append(liste['copropriete'][row])
        else:
            name_copropriete = 0
            while name_copropriete < len(names_coproprietes) and names_coproprietes[name_copropriete] != liste['copropriete'][row]:
                name_copropriete +=1
            if name_copropriete == len(names_coproprietes): 
                names_coproprietes.append(liste['copropriete'][row])
    return names_coproprietes                            

def recup_CP(Ville): 
    digit = ""
    ville = str(Ville)
    for char in range(len(ville)): 
        if ville[char].isdigit(): 
            digit += ville[char]
        if ville[char] == ' ' and len(digit) == 5:
            break  
    return digit         


# on trie les adresses recu de la résidence on en fait des mots clés et on verifie _ on recoi les adresses une à une
def residence_principale(liste_csv, adresse_copropriete, nom_immeuble):
    # on sépare l'adresse du CP et de la ville
    char = len(adresse_copropriete)-1
    adresse = adresse_copropriete
    CP_ville = ""
    digit = 0 
    while char != 0:
        if adresse[char].isdigit():
            digit += 1
            if digit == 5:
                adresse_copropriete = adresse[:char-1]
                CP_ville = adresse[char:]
                break
        elif adresse[char] == ' ':
            pass
        else :
            digit = 0 
        char -= 1
    
    # on récupère une liste des mots clés sur l'adresse : 
    not_key_word=[ 'rue', 'du', 'le', 'route', 'de', 'la', 'allee', 'des', 'avenue', 'av', 'bd', 'des', 'apt', 'square', 'les', 'residence', 'sur', 'bld', 'boulevard', 'av.', 'quai', 'chemin', 'cours', 'ter', 'res', 'au', 'aux', 'l', 'parc', 'impasse', 'imp', 'd', 'place', 'pl', 'allée']
    key_word = []
    adresse = str(adresse_copropriete).split()
    for word in adresse :
            word = word.replace(',','')
            if word.isdigit(): 
                continue
            elif len(word) < 3:
                continue
            elif word.lower() not in not_key_word : 
                 key_word.append(word.lower())
    
    # On compare l'adresse de la copro au copropriétaire de liste_copropriétaires
    liste = pd.read_csv(liste_csv, delimiter=';', encoding='latin-1', dtype='str')

    for row in range(len(liste)): 
         if nom_immeuble == liste.loc[row,'copropriete'] : 
            #on va récupérer les CP de la copro et du copropriétaire : 
            CP_copro = recup_CP(CP_ville)
            CP_coproprietaire = recup_CP(liste.loc[row,'ville'])
            if str(CP_copro) == str(CP_coproprietaire) : 
                # on compare la liste adresse copropriétaire avec celle de adresse copropriété 
                adresse = str(liste.loc[row,'adresse']).lower().split()
                for word in key_word : 
                    if word in adresse : 
                        liste.loc[row,'RP'] = 'Oui'

    df = pd.DataFrame(liste)
    return df
        



adresse_copropriete = "8 Rue de la Rousse, 35 400 Saint-Malo"
nom_immeuble = "CHAMPLAIN"
liste_csv = "liste champlain user.csv"
liste_copro = residence_principale(liste_csv, adresse_copropriete, nom_immeuble)
liste_copro.to_csv("liste champlain user.csv", encoding='latin-1')
                 




















'''
    # on fait des mots clés avec l'adresse de l'immeuble
    key_word = [] #mots clés de l'adresse de l'immeuble (sans CP ou numéro)
    adresse_copropriete += " " #pour controler le dernier mot 
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

    # on défini liste_csv 
    liste = pd.read_csv(liste_csv, delimiter=';', encoding='latin-1', dtype='str')
    liste.columns = ['code_coproprietaire','Nom','civilite','code_copropriete', 'copropriete','adresse','ville','RP','tel1','tel2','tel3', 'mail1','mail2','mail3','informations1','informations2','informations3', 'lot_logement','n_lot/n_plan/localisation(bat,esc,etg,pt)','lot_professionnel','lot_autre']
                
    # on liste les copropriétaires dans liste_csv on vérifie ceux de l'immeuble puis ceux de la ville de l'immeuble puis l'adresse 
    for row in range(len(liste)):
        if liste['copropriete'][row] == nom_immeuble: 
            ville_coproprietaire = str(liste['ville'][row])
            CP_coproprietaire= ''
            for char in range(len(ville_coproprietaire)): 
                if 47 < ord(ville_coproprietaire[char]) < 58 : 
                    CP_coproprietaire += ville_coproprietaire[char]
                elif ville_coproprietaire[char] == ' ': 
                    continue
                else: 
                    break
            if CP_coproprietaire == CP: 
                adresse_coproprietaire = liste['adresse'][row]
                list_adresse_coproprietaire = str(adresse_coproprietaire).split()
                for word_copropriete in range(len(key_word)): 
                    for word_coproprietaire in range(len(list_adresse_coproprietaire)):
                        word_coproprietaire_verif = list_adresse_coproprietaire[word_coproprietaire]
                        key_word_copropriete = key_word[word_copropriete]
                        if word_coproprietaire_verif.lower() == key_word_copropriete.lower(): 
                            liste['RP'][row] = "Oui"
                            break # on pourrait amelliorer la rapidité pour qu'il se coupe ici dès qu'il y a trouvé un mot similaire. car il coupe que la deuxième boucle 
        else: 
            continue
    
    df = pd.DataFrame(liste)
    df.to_csv('liste_coproprietaires.csv', sep=';', index=False)
    return 'liste_coproprietaires.csv'
'''

