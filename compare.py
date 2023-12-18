import pandas as pd
import numpy as np
import re

def compare_list(liste_ics, liste_user):
    copro_ics = pd.read_csv(liste_ics,  delimiter=';', encoding='latin-1', dtype='str')
    copro_user = pd.read_csv(liste_user,  delimiter=';', encoding='latin-1', dtype='str') 
    
    code_coproprietaire = ''
    code_copropriete = ''
    # on verifie que les colonnes utile à la comparaison sont présentes 
    # je suis obligé de faire une boucle car les colones intègre certaine fois des caractères spéciaux dans le titre de la colone 
    for col in copro_user.columns : 
        if re.search('code_coproprietaire', col):
            code_coproprietaire = col
        if re.search('code_copropriete', col):
            code_copropriete = col
    if len(code_coproprietaire) == 0 : 
        return 'code_coproprietaire'
    if len(code_copropriete) == 0 :
        return 'code_copropriete'
    # on ajoute les colonnes de l'user à ics : 
    new_col = []
    for col, indexcol in zip(copro_user.columns, range(len(copro_user.columns))) : 
        if col not in copro_ics.columns: 
            new_col.append(col)
            copro_ics.insert(indexcol, col, [np.nan]*len(copro_ics))


    # on compare les code_copropriétaire et code_copropriété pour trouver les mêmes noms est transmettre les info des nouvelles colonnes 
    for row in range(len(copro_ics)): 
        if copro_ics['code_coproprietaire'][row] in copro_user[code_coproprietaire].values :
            #on accède à la row ou on trouve le code copro puis on lui réplique les nouvelles colonnes :
            code_du_copropriétaire = copro_ics['code_coproprietaire'][row]
            row_user = copro_user.index[copro_user[code_coproprietaire].str.contains(code_du_copropriétaire)].tolist()
            # on va vérifier que la liste row_user récupère le bon copro dans la bonne copro : 
            for n in row_user: 
                if copro_ics['code_copropriete'][row] == copro_user[code_copropriete][n]:
                    for col in new_col : 
                        copro_ics.loc[row, col] = copro_user.loc[n, col]
                    break

    # verifier que copro_ics ne contient pas des colonnes supprimées par l'user 
    for col in copro_ics.columns: 
        if col not in copro_user.columns :
           copro_ics.drop([col], axis=1, inplace=True)


    copro_ics.to_csv('liste_coproprietaires.csv', sep=';', index=False)
    return 'liste_copropriétaires.csv'