import pandas as pd
import unicodedata
from pandas import *

def nettoyer_caracteres(indata): 
    if isinstance(indata, str): 
        indata = indata.encode('latin-1', 'ignore').decode('latin-1')
    return indata 

def transform_file(csvfile):
    # charger les fichiers excel et changer le nom des colonnes  
    fichier = csvfile
    if len(fichier.columns) == 3 : 
        fichier.columns= ['coproprietaires', 'immeubles', 'coordonnees']
    elif len(fichier.columns) == 4 :
         fichier.columns= ['coproprietaires', 'immeubles', 'coordonnees', '']

    # Nettoyage des caractères non traitable
    for column in fichier.columns : 
        fichier[column] = fichier[column].apply(nettoyer_caracteres)

    #définition de toutes mes colonnes
    data= []
    for row in range(len(fichier)):
        if not pd.isnull(fichier['coproprietaires'][row]):
            columns = {
                'code_coproprietaire': '',
                'Nom': '',
                'civilite': '',
                'code_copropriete': '',
                'copropriete': '',
                'adresse': '',
                'ville': '',
                'RP':'Non',
                'tel1':'',
                'tel2':'',
                'tel3':'',
                'mail1':'',
                'mail2':'',
                'mail3':'',
                'informations1':'',
                'informations2':'',
                'informations3':'',
                'lot_logement':'',
                'n_lot/n_plan/localisation(bat,esc,etg,pt)':'',
                'lot_professionnel':'',
                'lot_autre':'',
            }
            data.append(columns)

    # fonction conservant la char n+2 pour la vérif dans hash_copropriétaire
    def NextChar(column, letter):
        prochain_char = ""
        if letter+1 < len(column):
            prochain_char = column[letter+1]
        return prochain_char

    #séparer 'coproprietaires'
    def hash_coproprietaires(column, row):
        letter = 0
        civi = 0
        while column[letter].isdigit():
                data[row]['code_coproprietaire'] += str(column[letter])
                letter +=1
        #ici je met letter+1 car je ne veux pas prendre le premier espace ni le dernier avant le ( ou ''
        while column[letter+1] != '(' and column[letter+1] != '':
                data[row]['Nom'] += column[letter+1]
                letter += 1
                if letter+1 >= len(column):
                    return

        if column[letter+1] != '':
            letter+=1
            while column[letter] != ')' and column[letter] != '':
                char = column[letter]
                prochain_char = NextChar(column, letter)
                # Si c'est un M en fonction de la lettre qui suit c'est soit Mme ou M
                if char == 'M':
                    if prochain_char == 'm' or prochain_char == 'a':
                        if civi == 0:
                            data[row]['civilite'] += 'Mme'
                            civi = 1
                        else:
                            data[row]['civilite'] += '/Mme'
                    elif prochain_char == ' ' or prochain_char == '.' or prochain_char == 'r' or prochain_char == 'o':
                        if civi == 0:
                            data[row]['civilite'] += 'M'
                            civi = 1
                        else:
                            data[row]['civilite'] += '/M'
                    else:
                        if civi == 0:
                            data[row]['civilite'] += 'M'
                            civi = 1
                        else:
                            data[row]['civilite'] += '/M'
                if char.upper() == 'I' and civi == 0:
                    data[row]['civilite'] += 'Indivision'
                    break
                   
                if char.upper() == 'S' and civi == 0:
                    if prochain_char.upper() == 'O':
                        data[row]['civilite'] += 'Societe'
                        break
                    else:
                        data[row]['civilite'] += 'Succession'
                        break
               
                if letter+1 >= len(column):
                    return
                letter +=1
               
                           
    def hash_copropriété(column, row):
        letter = 0
        entre_nom_copro = 0
        while letter < len(column): 
                char = column[letter]
                if 47<ord(char)<58 and entre_nom_copro == 0 : 
                    data[row]['code_copropriete'] += char
                elif 64 <ord(char)< 91 or 96 <ord(char)< 123 or 47<ord(char)<58 and entre_nom_copro == 1:
                    data[row]['copropriete'] += char
                    entre_nom_copro = 1
                elif char == ' ' and entre_nom_copro == 1: 
                    data[row]['copropriete'] += char
                letter += 1

    #verifie s'il y a des doublons de mail ou tel dans les infos d'un copropriétaire
    def doublon(list, columne, nombre):
        t1 = 0
        while t1 < nombre:
            t2 = t1+1
            while t2 < nombre:
                if list[t1][columne] != list[t2][columne]:
                    t2 += 1
                else:
                    del list[t1]
                    t1 = -1 # on met moins un car revient à 0 ligne 146 pour tout retester
                    nombre-=1
                    break
            t1 +=1
        return list

    #On envoie les coordonnées vers data
    def SendToData(list, columnlist, columnedata, row):
        n = 0
        N = len(list)
        while n < N:
            if columnlist == 'adresse' or columnlist == 'ville':
                data[row][columnlist] = list[n][columnlist]
                return
            else :
                if n < 3:
                    data[row][columnedata[n]] = list[n][columnlist]
            n+=1
    
    def remove_accent(coordonnee): 
        return unicodedata.normalize('NFKD', coordonnee).encode('ASCII', 'ignore').decode('utf-8', 'ignore')

    def add_to_list(list, coordonnee, categorie, information):
        coordonnee = remove_accent(coordonnee)
        liste_mail = coordonnee.split("(")
        #ajouter la coordonnée à la liste
        liste_mail[0] = str(liste_mail[0]).strip()
        if categorie == 'numéro' :
            liste_mail[0] = str(liste_mail[0]).replace(' ', '.')
        donnée = {
            categorie:liste_mail[0],
        }
        list.append(donnée)
        #ajouter à info ce qu'il y a après la parenthèse si l'info est plus grande que 14
        if len(liste_mail) > 1:
            if len(liste_mail[1]) > 15 :
                info = str(liste_mail[1]).strip('('' '')') #on supprime les espaces au début et à la fin ainsi que la '('et ')'
                donnée ={
                    'info': info,
                }
                information.append(donnée)
        return list, information


    def hash_coordonnées(column, row):
        #listes de stockages de coordonnées
        Email= []
        tel= []
        information= []
        adresse_P=[]
        ville=[]
        # on sépare les ! et les / avant une ') ':
        column = column.replace(") /", "!")
        list_coordonnees = column.split('!')

        #je vérifie chaque type de coordonnées
        for coordonnee in list_coordonnees :
            coordonnee = coordonnee.strip()

        # on cherche à verifier si c'est un num en comptant le nombre de chiffre
            digit = 0 
            for char in coordonnee:
                if char.isdigit() :
                    digit += 1 

            if "@" in coordonnee :
                add_to_list(Email,coordonnee,'mail',information)
           
            elif digit > 9 :
                add_to_list(tel,coordonnee,'numéro',information)

           
            elif "(" not in coordonnee :
                if len(adresse_P) == 0 :
                    #verifier si add_to_list n'est pas out of range car il n'y a pas de '('
                    add_to_list(adresse_P, coordonnee, 'adresse', information)
                else :
                    add_to_list(ville, coordonnee, 'ville', information)
            
            else : 
                add_to_list(information, coordonnee, 'info', information)
           
        # si on a pas de ville et une adresse alors on doit sortir la ville de adresse
        if len(adresse_P) > 0 and len(ville) == 0 :
            char = len(adresse_P[0]['adresse']) - 1 
            adresse = adresse_P[0]['adresse']
            digit = 0
            # on fait une boucle inversé pour trouver les 5 derniers chiffres à la suite
            while char != 0 :
                if adresse[char].isdigit() :
                    digit += 1
                    if digit == 5 :
                        adresse_P[0]['adresse'] = adresse[:char-1]
                        CP_ville = adresse[char:]
                        add_to_list(ville, CP_ville, 'ville', information)
                        break
                elif adresse[char] == ' ':
                    pass
                else :
                    digit = 0 
                char -= 1


        # Une fois trié je vais vérifier que deux coordonnées ne sont pas similiaire si c'est le cas je la supprime
        tel = doublon(tel, 'numéro', len(tel))
        Email = doublon(Email, 'mail', len(Email))
        information = doublon(information, 'info', len(information))
        # j'envoie chaque liste dans data
        columnTel=['tel1','tel2','tel3']
        columnMail=['mail1','mail2','mail3']
        columninfo=['informations1','informations2','informations3']
        columnadresse = ['adresse']
        columnville = ['ville']
        SendToData(tel, 'numéro', columnTel, row)
        SendToData(Email, 'mail', columnMail, row)
        SendToData(information, 'info', columninfo, row)
        SendToData(adresse_P, 'adresse', columnadresse, row )
        SendToData(ville, 'ville', columnville, row)
   
    # Lire chaque ligne du csv et remettre sur la même ligne les coordonnées
    row = 0
    i = 1 
    while i < len(fichier):
        if not pd.isnull(fichier['coproprietaires'][i]):
            last_row = fichier.loc[i]
        else:
            coordonnees = str(last_row['coordonnees'])
            if not pd.isnull(fichier['coordonnees'][i]):
                Newcoordonnees = str(fichier['coordonnees'][i])
                last_row['coordonnees'] = coordonnees+" ! "+Newcoordonnees
       
    #envoie chaque ligne au hash pour trier chaque colonne
        if i+1 < len(fichier):
            if not pd.isnull(fichier['coproprietaires'][i+1]):
                #maintenant tout est sur la même ligne on va trier les informations
                hash_coproprietaires(last_row['coproprietaires'], row)
                hash_copropriété(last_row['immeubles'], row)
                hash_coordonnées(last_row['coordonnees'], row)
                row += 1
               
        elif i+1 == len(fichier):
            #maintenant tout est sur la même ligne on va trier les informations
            hash_coproprietaires(last_row['coproprietaires'], row)
            hash_copropriété(last_row['immeubles'], row)
            hash_coordonnées(last_row['coordonnees'], row)
            row += 1

        i=i+1

    #on remplace notre ancien fichier par les données de data
    df = pd.DataFrame(data)
    return df
