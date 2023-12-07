import pandas as pd

def compare_list(liste_ics, liste_user): 
    copro_ics = pd.read_csv(liste_ics,  delimiter=';', encoding='latin-1')
    copro_user = pd.read_csv(liste_user,  delimiter=';', encoding='latin-1') 
    #test
    copro_vendu = []
    #fin test
    for row_u in range(len(copro_user)): 
        trouve = 0
        copropriete_trouve = 0
        for row_i in range(len(copro_ics)): 
            #on doit vérifier la copro aussi car un copro peut se trouver dans deux immeubles 
            copropriete_u = str(copro_user['code_copropriete'][row_u]).lower().split()
            copropriete_i = str(copro_ics['code_copropriete'][row_i]).lower().split()
            coproprietaire_u = copro_user['code_coproprietaire'][row_u]
            coproprietaire_i = copro_ics['code_coproprietaire'][row_i]
            if copropriete_u == copropriete_i :
                copropriete_trouve = 1
                if coproprietaire_u == coproprietaire_i :  
                    trouve = 1
                    #on verifie que les informations sont toujours bonnes et on le supprime de copro_ics pour plus rapide: 
                    columns =['Nom','civilite','copropriete','adresse', 'ville','tel1','tel2','tel3','mail1','mail2','mail3','informations1','informations2','informations3']
                    for col in columns : 
                        if copro_user[col][row_u] != copro_ics[col][row_i]: 
                            copro_user[col][row_u] == copro_ics[col][row_i]
                    copro_ics.drop([row_i], inplace=True)
                    copro_ics.reset_index(drop=True, inplace=True)
                    break
        #on supprime les proprios plus présent dans copro_ics : 
        if trouve == 0 and copropriete_trouve == 1: 
            #test
            print("je passe bien ici")
            copro_vendu.append(copro_user.at[row_u, 'Nom'])
            #fin test
            copro_user.drop([row_u], inplace=True)
            copro_user.reset_index(drop=True, inplace=True)


    #pour tous les nouveaux copropriétaires présents dans copro_ics je veux ajouter uniquement les colonnes déjà présentes dans copro user :
    for row in range(len(copro_ics)): 
        ligneAajouter = copro_ics.iloc[row]
        for col in copro_user.columns : 
            lencopro_user = len(copro_user)
            copro_user.loc[lencopro_user, col] = ligneAajouter[col]
        copro_user.reset_index(drop=True, inplace=True)
    
    copro_user = copro_user.sort_values(by=['code_copropriete', 'Nom'])

    #test
    copro_ics.to_csv('liste_user.csv',  sep=';', index=False)
    df = pd.DataFrame(copro_vendu)
    df.to_csv('liste_vendu.csv',  sep=';', index=False)
    #fin test

    copro_user.to_csv('liste_coproprietaires.csv', sep=';', index=False)
    return 'liste_copropriétaires.csv'

                
                


#verifier que les anciens se supprime et que les nouveaux s'ajoute et que les adresses ou autre infos changes. 


            

