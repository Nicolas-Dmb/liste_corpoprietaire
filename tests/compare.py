import pandas as pd
import numpy as np

def compare_list(liste_ics, liste_user): 
    copro_ics = pd.read_csv(liste_ics,  delimiter=';', encoding='latin-1', dtype='str')
    copro_user = pd.read_csv(liste_user,  delimiter=';', encoding='latin-1', dtype='str') 
    #test
    copro_vendu = []
    #fin test
    lencopro_user = len(copro_user)
    row_u = 0
    while row_u < lencopro_user: 
        trouve = 0
        copropriete_trouve = 0
        #lencopro_ics = len(copro_ics)
        for row_i in range(len(copro_ics)): 
            #on doit vérifier la copro aussi car un copro peut se trouver dans deux immeubles 
            copropriete_u = copro_user['code_copropriete'][row_u]
            copropriete_i = copro_ics['code_copropriete'][row_i]
            coproprietaire_u = copro_user['code_coproprietaire'][row_u]
            coproprietaire_i = copro_ics['code_coproprietaire'][row_i]
            if copropriete_u == copropriete_i :
                copropriete_trouve = 1
                if coproprietaire_u == coproprietaire_i :  
                    trouve = 1
                    #test
                    print(f"trouvé : {copro_user['Nom'][row_u]}")
                    #fin test 
                    #on verifie que les informations sont toujours bonnes et on le supprime de copro_ics pour plus rapide: 
                    columns =['Nom','civilite','copropriete','adresse', 'ville','tel1','tel2','tel3','mail1','mail2','mail3','informations1','informations2','informations3']
                    for col in columns : 
                        valeur = copro_ics.loc[row_i, col]
                        if pd.notna(valeur):
                            copro_user.loc[row_u, col] = copro_ics.loc[row_i, col]
                        else:
                            copro_user.loc[row_u, col] = np.nan
                    copro_ics.drop([row_i], inplace=True)
                    copro_ics.reset_index(drop=True, inplace=True)
                    break
        #on supprime les proprios plus présent dans copro_ics : 
        if trouve == 0 and copropriete_trouve == 1: 
            #test
            print(f"vendu : {copro_user.at[row_u, 'Nom']}")
            row = {"nom":f"{copro_user.at[row_u, 'Nom']}"}
            copro_vendu.append(row)
            #fin test
            copro_user.drop([row_u], inplace=True)
            copro_user.reset_index(drop=True, inplace=True)
            lencopro_user = len(copro_user)
            row_u -=1
        row_u += 1


    #pour tous les nouveaux copropriétaires présents dans copro_ics je veux ajouter uniquement les colonnes déjà présentes dans copro user :
    for row in range(len(copro_ics)): 
        ligneAajouter = copro_ics.iloc[row]
        #ligneAajouter = ligneAajouter.astype("string")
        #test 
        print(f"nouveau: {ligneAajouter['Nom']}")
        #fin test 
        lencopro_user = len(copro_user)
        for col in copro_user.columns :
            if col in ligneAajouter: 
                #ici j'envisage le fait que certaine colonne ne soit pas créée dans liste_ics il faut donc dans ce cas le fair de cette manière : 
                valeur = ligneAajouter[col]
                if pd.notna(valeur):  # Vérifiez si la valeur n'est pas NaN
                    copro_user[col] = copro_user[col].astype('str')
                    copro_user.loc[lencopro_user, col] = str(valeur)
                else:
                    copro_user.loc[lencopro_user, col] = np.nan  # Valeur "" pour les NaN dans la série
            else: 
                break
        copro_user.reset_index(drop=True, inplace=True)
    
    copro_user = copro_user.sort_values(by=['code_copropriete', 'Nom'])

    #test
    copro_ics.to_csv('liste_user.csv',  sep=';', index=False)
    df = pd.DataFrame(copro_vendu)
    df.to_csv('liste_vendu.csv',  sep=';', index=False)
    #fin test

    copro_user.to_csv('liste_coproprietaires.csv', sep=';', index=False)
    return 'liste_copropriétaires.csv'

                
                
liste = compare_list('liste_ics.csv', 'liste_user.csv')

#verifier que les anciens se supprime et que les nouveaux s'ajoute et que les adresses ou autre infos changes. 


            

