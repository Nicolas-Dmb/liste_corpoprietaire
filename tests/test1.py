import pandas as pd

def transform_file(csvfile):
    # chargé les fichiers excel et changer le nom des colonnes  
    fichier = csvfile
    fichier.columns= ['coproprietaires', 'immeubles', 'coordonnees']

    # trier dans un dictionnaire chaque copropriétaire
        #variable de la boucle
    rows = len(fichier)
    column=['coproprietaires', 'immeubles', 'coordonnees']
    columns=len(column)

    #définition de toutes mes colonnes de mon futur tableau 
    data= []
    for row in range(rows) : 
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
                'n°_lot/n°_plan/loca(bât,esc,etg,pt)':'',
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
                if 47<ord(char)<58 : 
                    data[row]['code_copropriete'] += char
                elif 64 <ord(char)< 91 or 96 <ord(char)< 123:
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
                data[row][columnedata[n]] = list[n][columnlist]
                return
            else : 
                if n < 3:
                    data[row][columnedata[n]] = list[n][columnlist]
            n+=1

    def hash_coordonnées(column, row):
        letter = 0
        adresse = False
        city = False
        i=0 #nombre de / sur la ligne 
        coordonnee= [{'mail_numero':'',}]
        M = 0 #Nombre de mail sur la ligne 
        T = 0 #Nombre de tel sur la ligne 
        Inf = 0 #Nombre d'information pertinente
        A = 0 #Nombre d'adresse en théorie 1
        V = 0 #Nombre de ville  en théorie 1
        Email= []
        tel= []
        information= []
        adresse_P=[]
        ville=[]
        # Je sépare chaque coordonnée de la ligne 
        while letter < len(column):
            char = column[letter]
            if char == '!': 
                i +=1
                donnee = {
                    'mail_numero':'',
                }
                coordonnee.append(donnee)
            else: 
                coordonnee[i]['mail_numero'] += char
            letter+=1
        # Pour chaque coordonnée de la ligne 
        y = 0 #situe la coordonnée à laquelle on se situe 
        for y in range(i+1): #je me +1 car le i rpz le nombre de / mais il y a une coordonnée avant le / 
            #Je copie la coordonnée  
            info = coordonnee[y]['mail_numero']
            # on dissocie la coordonnées de l'info
            x=0 #nombre de char pour la coordonnée nommé info 
            parenthese = 0
            TelMail= str('') #receuille une coordonnée un mail ou un tel 
            detail= str('') #recueille une info à récupérer ou non 
            leninfo = len(info)
            caractère = 0
            while x < leninfo:
                if info[x] == '(': 
                    parenthese = 1
                elif parenthese == 0: 
                    if x == 0 and info[x] == ' ':
                        parenthese = 0
                    elif info[x] == ' ': 
                        if x+1 == leninfo :
                            parenthese = 0
                        elif info[x+1] == '(': 
                            parenthese = 0
                        elif 64 < ord(info[x-1].upper()) < 91 or 64 < ord(info[x+1].upper()) < 91 : 
                            TelMail += ' '
                        else: 
                            if caractère == 1: 
                                parenthese = 0
                            else : 
                                TelMail += '.'
                    elif 0 <= x <= leninfo-1 and info[x] != '': 
                        TelMail += info[x]
                    if 64 < ord(info[x].upper()) < 91 : 
                        caractère = 1
                elif parenthese == 1:
                    if info[x] == ')':
                        parenthese = 1
                    else:
                        detail += info[x]
                x += 1
            #puis je vérifie si c'est un mail ou un tel 
            mail = 0#permet de savoir si c'est un mail ou un tel
            lenTelMail= len(TelMail) 
            for char in range(lenTelMail): 
                if TelMail[char]=='@': 
                    mail = 1
                    adresse_mail = {
                    'mail':'',
                    }
                    Email.append(adresse_mail)
            # si mail égale 1 alors j'inscit dans la liste le mail 
            if mail == 1: 
                Email[M]['mail']=TelMail
                M +=1
            # sinon j'inscrit dans ma liste de tel 
            elif mail == 0: 
                #on vient vérifier que c'est que des chiffres ou des espaces mais pas des lettre maj ou min
                num_tel = 0 #compte le nombre de chiffre dans le TelMail
                num_letter = 0 #compte le nombre de chiffre dans le TelMail
                # je dois mettre ca au cas ou il y ait des coordonnées de prises en compte s'il y a un espace et donc telmail = 'nan' ou ''. 
                if TelMail == 'nan': 
                    lenTelMail = 0
                    parenthese = 1
                for char in range(lenTelMail):
                    if 47 < ord(TelMail[char]) < 58 :
                        num_tel+=1
                    else : 
                        num_letter +=1
                if num_tel > 9 and parenthese==1 : #on vient récup que les tels car il y a forcément une parenthèse
                    numero={
                        'telephone':'',
                    }
                    tel.append(numero)
                    tel[T]['telephone']=TelMail
                    T += 1
                elif parenthese == 0 :
                    if adresse == False: 
                        detail_ad ={
                            'adresse':'',
                        }
                        adresse_P.append(detail_ad)
                        adresse_P[A]['adresse']=TelMail
                        A = 1 # on ne met pas +1 car il faut uniquement une adresse
                        adresse=True
                    elif adresse == True: 
                        detail_ville ={
                            'ville':'',
                        }
                        ville.append(detail_ville)
                        ville[V]['ville']=TelMail
                        V = 1 # on ne met pas +1 car il faut uniquement une ville 
                        city = True
                elif num_letter > 14: #sinon on le met dans info et non tel
                    precision = {
                    'info':'',
                    }
                    information.append(precision)
                    information[Inf]['info']=TelMail
                    Inf += 1 
            # Je vais traité les info des coordonnées (les info pertinnennte sont plus longue que 13 char)
            if len(detail) > 14 :
                precision = {
                    'info':'',
                }
                information.append(precision)
                information[Inf]['info']=detail
                Inf += 1 
            y += 1
        
            # J'ai maintenant deux liste avec l'une comptenant l'adresse et peut-être la ville et l'autre comptenant la ville si sur deux lignes. 
        # Je vais vérifier que si l'adresse est complété alors la ville aussi elle doivent toutes les deux être égale à 1 
        if adresse == True and city == False :
            code_postale = adresse_P[0]['adresse']
            new_adresse = ''
            code = False
            char = 0
            new_code =''
            while char < len(code_postale):
                if code == False :  
                    if 47 < ord(code_postale[char]) < 58: 
                        new_code =''
                        while char < len(code_postale): 
                            if 47 < ord(code_postale[char]) < 58 and len(new_code) == 4:
                                new_code += code_postale[char]
                                code = True
                                char += 1 
                                break
                            elif 47 < ord(code_postale[char]) < 58:
                                new_code += code_postale[char]
                                char += 1 
                                continue
                            elif code_postale[char] == ' ': 
                                new_code += code_postale[char] 
                                char +=1
                                continue
                            else :
                                new_adresse += new_code 
                                new_adresse += code_postale[char]
                                char +=1
                                new_code =''
                                break
                    else : 
                        new_adresse += code_postale[char]
                        char += 1
                elif code == True: 
                    new_code += code_postale[char]
                    char += 1
            #permet d'éviter de garder dans ville les derniers chiffres d'une adresse
            if code == False: 
                new_adresse += new_code
                new_code = ''
            #on créer copy la nouvelle adresse dans adresse_P et on créer la colonne dans ville avec sa valeur new_code quelle existe ou non. 
            adresse_P[0]['adresse'] = new_adresse
            detail_ville ={
                'ville':'',
            }
            ville.append(detail_ville)
            ville[0]['ville'] = new_code
            V = 1

                # Sinon cela veut dire que l'adresse comptient aussi la ville 
                        # je devrais donc recherche une suite de 5 chiffres si je l'ai alors tout ce qui vient à partir du premier chiffre de la suite vient dans ville
            # Pas besoin de vérifier les doublons mais trouver les RP puis ajouter les colonnes villes et adresse. 
        # Une fois trié je vais vérifier que deux coordonnées ne sont pas similiaire si c'est le cas je la supprime
        tel = doublon(tel, 'telephone', T)
        Email = doublon(Email, 'mail', M)
        information = doublon(information, 'info', Inf)

        # j'envoie chaque liste dans data
        columnTel=['tel1','tel2','tel3']
        columnMail=['mail1','mail2','mail3']
        columninfo=['informations1','informations2','informations3']
        columnadresse = ['adresse']
        columnville = ['ville']
        SendToData(tel, 'telephone', columnTel, row)
        SendToData(Email, 'mail', columnMail, row)
        SendToData(information, 'info', columninfo, row)
        SendToData(adresse_P, 'adresse', columnadresse, row )
        SendToData(ville, 'ville', columnville, row)




        # Lire chaque ligne du csv et remettre sur la même ligne les coordonnées 
    row = 0
    i = 1 
    while i < rows:
        if not pd.isnull(fichier['coproprietaires'][i]):
            last_row = fichier.loc[i]
        else: 
            coordonnees = str(last_row['coordonnees'])
            Newcoordonnees = str(fichier['coordonnees'][i])
            last_row['coordonnees'] = coordonnees+" ! "+Newcoordonnees
        
    #envoie chaque ligne au hash pour trier chaque colonne 
        if i+1 < rows :
            if not pd.isnull(fichier['coproprietaires'][i+1]):
                #maintenant tout est sur la même ligne on va trier les informations 
                #print (last_row)
                #print ('prochaine row\n')
                hash_coproprietaires(last_row['coproprietaires'], row)
                hash_copropriété(last_row['immeubles'], row)
                hash_coordonnées(last_row['coordonnees'], row)
                row += 1
                
        elif i+1 == rows:
            #maintenant tout est sur la même ligne on va trier les informations 
            hash_coproprietaires(last_row['coproprietaires'], row)
            hash_copropriété(last_row['immeubles'], row)
            hash_coordonnées(last_row['coordonnees'], row)
            row += 1

        i=i+1


    # on peut maintenant supprimer puis pousser les datas vers le fichier csv 
    #on supprime les colonnes 
    for col in range(len(column)): 
        fichier.pop(column[col])

    #on ajoute les nouvelles colonnes 

    #on ajoute les rows 
    #columns=['code_coproprietaire','Nom','Prenom','civilite','code_copropriete','copropriete','tel1','tel2','tel3','mail1','mail2','mail3','informations1','informations2','informations3']
    #for col in range(len(columns)): 
        #fichier.insert(col, columns[col],'', allow_duplicates=False)
    df = pd.DataFrame(data)
    #print (fichier)
    df.to_csv('tests/liste_coproprietaires.csv', sep=';', index=False)
    return 'tests/liste_coproprietaires.csv'