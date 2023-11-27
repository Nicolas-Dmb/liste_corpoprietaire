def names_coproprietes(liste_csv):
    names_coproprietes=[]
    for copropriete in range(len(liste_csv)):
        if copropriete == 0 :
            names_coproprietes.append(liste_csv[copropriete]['copropriete'])
        else: 
            name_copropriete = 0
            while name_copropriete < len(names_coproprietes) and names_coproprietes[name_copropriete] != liste_csv[copropriete]['copropriete']:
                name_copropriete +=1
            if name_copropriete == len(names_coproprietes): 
                names_coproprietes.append(liste_csv[copropriete]['copropriete'])
    return names_coproprietes                            
                
# on trie les adresses recu de la résidence on en fait des mots clés et on verifie _ on recoi les adresses une à une
def residence_principale(liste_csv, adresse_copropriete, nom_immeuble):
    # on fait des mots clés avec l'adresse de l'immeuble
    key_word = [] #mots clés de l'adresse de l'immeuble (sans CP ou numéro)
    CP = ''
    not_key_word=[ 'rue', 'du', 'le', 'route', 'de', 'la', 'allee', 'des', 'avenue', 'av', 'bd', 'des', 'apt', 'square', 'les', 'residence', 'sur', 'bld', 'boulevard', 'av.', 'quai', 'chemin', 'cours', 'ter', 'res', 'au', 'aux', 'l', 'parc', 'impasse', 'imp', 'd', 'place', 'pl']
    word_inprogress =''
    typeOfstring = ''
    lenOfword = 0
    for char in range(len(adresse_copropriete)): 
        if 47 < ord(adresse_copropriete[char]) < 58: 
            word_inprogress += str(adresse_copropriete[char])
            typeOfstring = 'int'
            lenOfword += 1
        elif 96 < ord(adresse_copropriete[char].lower()) < 123: 
            word_inprogress += str(adresse_copropriete[char].lower())
            typeOfstring = 'str'
            lenOfword += 1
        elif adresse_copropriete[char] == ' ':
            next_char ='I'
            if char+1 < len(adresse_copropriete): 
                next_char = adresse_copropriete[char+1]
            if typeOfstring == 'int' and lenOfword == '5':
                CP = word_inprogress
            elif typeOfstring == 'int' and lenOfword == '2' and 47 < ord(next_char) < 58 :
                continue
            elif typeOfstring == 'str': 
                for word in range(not_key_word): 
                    if not_key_word[word] == word_inprogress: 
                        word_inprogress=''
                if word_inprogress != '': 
                    key_word.append(word_inprogress)
        else: 
            continue

                
    # on liste les copropriétaires dans liste_csv on vérifie ceux de l'immeuble puis ceux de la ville de l'immeuble puis l'adresse 
    for row in range(len(liste_csv)) :
        if liste_csv[row]['copropriete'] == nom_immeuble: 
            ville_coproprietaire = liste_csv[row]['ville']
            CP_coproprietaire= ''
            for char in range(len(ville_coproprietaire)): 
                if 47 < ord(ville_coproprietaire[char]) < 58 : 
                    CP_coproprietaire += ville_coproprietaire[char]
                elif ville_coproprietaire[char] == ' ': 
                    continue
                else: 
                    break
            if CP_coproprietaire == CP: 
                adresse_coproprietaire = liste_csv[row]['adresse'] 
                list_adresse_coproprietaire = adresse_copropriete.split()
                for word_coproprietaire in range(len(list_adresse_coproprietaire)):
                    for word_copropriete in range(len(key_word)): 
                        if list_adresse_coproprietaire[word_coproprietaire].lower == key_word[word_copropriete].lower: 
                            liste_csv[row]['RP'] = "Oui"
        else: 
            continue
    
    return 'liste_csv'

