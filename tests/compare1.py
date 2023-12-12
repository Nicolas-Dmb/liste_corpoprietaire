import pandas as pd
import numpy as np

def compare_list(liste_ics, liste_user): 
    copro_ics = pd.read_csv(liste_ics,  delimiter=';', encoding='latin-1', dtype='str')
    copro_user = pd.read_csv(liste_user,  delimiter=';', encoding='latin-1', dtype='str') 
    
    # on verifie que les colonnes utile à la comparaison sont présentes 
    if 'code_coproprietaire' not in copro_user.columns : 
        return 'code_copropriétaire'
        print("la colonne 'code_copropriétaire' n'est pas présente dans votre liste impossible de mettre à jour le fichier")
  
    if 'code_copropriete' not in copro_user.columns : 
        return 'code_copropriété'
        print("la colonne 'code_copropriete' n'est pas présente dans votre liste impossible de mettre à jour le fichier")

    # on ajoute les colonnes de l'user à ics : 
    new_col = []
    for col, indexcol in zip(copro_user.columns, range(len(copro_user.columns))) : 
        if col not in copro_ics.columns: 
            new_col.append(col)
            copro_ics.insert(indexcol, col, [np.nan]*len(copro_ics))


    # on compare les code_copropriétaire et code_copropriété pour trouver les mêmes noms est transmettre les info des nouvelles colonnes 
    for row in range(len(copro_ics)): 
        if copro_ics['code_coproprietaire'][row] in copro_user['code_coproprietaire'].values :
            #on accède à la row ou on trouve le code copro puis on lui réplique les nouvelles colonnes :
            code_du_copropriétaire = copro_ics['code_coproprietaire'][row]
            row_user = copro_user.index[copro_user["code_coproprietaire"].str.contains(code_du_copropriétaire)].tolist()
            # on va vérifier que la liste row_user récupère le bon copro dans la bonne copro : 
            for n in row_user: 
                if copro_ics['code_copropriete'][row] == copro_user['code_copropriete'][n]:
                    for col in new_col : 
                        copro_ics.loc[row, col] = copro_user.loc[n, col]
                    break

    # verifier que copro_ics ne contient pas des colonnes supprimées par l'user 
    for col in copro_ics.columns: 
        if col not in copro_user.columns :
           copro_ics.drop([col], axis=1, inplace=True)


    copro_ics.to_csv('liste_coproprietaires.csv', sep=';', index=False)
    return 'liste_copropriétaires.csv'

                
                
liste = compare_list('liste_ics.csv', 'liste_user.csv')