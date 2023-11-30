import pandas as pd 
from test1 import *

# tri la colonne lot du fichier CSV et exporte vers notre nouvelle liste les nouvelles colonnes n°lot et type de lot
def col_lot(data_lot_lot,data_lot_plan,data_lot_loc, row, new_data_lot): 
    first_space = 0
    data_lot_lot = str(data_lot_lot)
    for char in range(len(data_lot_lot)):
        data = str(data_lot_lot[char])
        if 47< ord(data) <58: 
            new_data_lot[row]['n°_lot-n°_plan-loca(bât,esc,etg,pt)'] += data
        # permet de ne pas prendre en compte l'espace entre le n° et le type de lot 
        elif first_space == 0: 
            first_space = 1
            continue
        else: 
            new_data_lot[row]['type_lot'] += data
    new_data_lot[row]['n°_lot-n°_plan-loca(bât,esc,etg,pt)'] += "/" + str(data_lot_plan) + "/" + str(data_lot_loc)
    return new_data_lot

def col_coproprietaire(data_lot, row, new_data_lot): 
    char = 0
    data_lot = str(data_lot)
    while char < len(data_lot) and data_lot[char] != '(': 
        new_data_lot[row]['coproprietaire'] += data_lot[char]
        char += 1
    return new_data_lot




def tri_liste_lot(liste_lot):
    new_data_lot=[]
    for row in range(len(liste_lot)):
        #on crée notre nouveau tableau dans new_data: 
        colonnes = { 'type_lot':'',
                    'coproprietaire':'',
                    'n°_lot-n°_plan-loca(bât,esc,etg,pt)':'',
                    }
        new_data_lot.append(colonnes)
        #on importe les nouvelles données 
        new_data_lot = col_lot(liste_lot['Lot'][row],liste_lot['NoPlan'][row],liste_lot['Bat-Esc-Etg-Pt'][row], row, new_data_lot)
        new_data_lot = col_coproprietaire(liste_lot['Coproprietaire'][row], row, new_data_lot)
        
    df = pd.DataFrame(new_data_lot)
    #print (fichier)
    df.to_csv('tests/liste_lots.csv', sep=';', index=False)
    return 'tests/liste_lots.csv'


def add_lot(liste_lot, liste_copro): 
    liste_lots = pd.read_csv(liste_lot, delimiter=';', encoding='latin-1')
    liste_copros = pd.read_csv(liste_copro, delimiter=';', encoding='latin-1')
# on vient ici mettre les lots en fonction du type de lot dans la colonne qui correspond au mm nom dans liste copro 
    # deux limites 
    # - si le copropriétaire est inscrit plusieurs fois dans la liste copro il y aura les même lot d'indiqué 
    # - si le copropriétaire à plus d'un apt plus d'un lot divers et plus d'un bien local commercial il n'apparaitra qu'un seul de chaque type 
    # - on ne distingue aucun immeuble ici car la liste lot n'affiche pas l'immeuble on regarde juste les noms si un copro est copro dans deux immeubles il sera affiche les lot d'un de ses immeubles sur les deux copro 
    # - 
    for row_c in range(len(liste_copros)):
        for row_l in range(len(liste_lots)): 
            name_liste_copro =str(liste_copros['Nom'][row_c]).lower().strip()
            name_liste_lot = str(liste_lots['coproprietaire'][row_l]).lower()
            name_liste_lot = name_liste_lot[:32]
            name_liste_lot = name_liste_lot.strip()
            if name_liste_lot == name_liste_copro :
                type_lot = str(liste_lots['type_lot'][row_l])
                local_lot = liste_lots['n°_lot-n°_plan-loca(bât,esc,etg,pt)'][row_l]
                if type_lot.lower() == 'appartement' or type_lot.lower() == 'studio' or type_lot.lower() == 'maison' or type_lot[0] == 'T': 
                    liste_copros['lot_logement'][row_c] = type_lot
                    liste_copros['n°_lot/n°_plan/loca(bât,esc,etg,pt)'][row_c] = local_lot
                elif type_lot.lower() == 'local commerc.' or type_lot.lower() == 'local activites' or type_lot.lower() == 'bureau': 
                    liste_copros['lot_professionnel'][row_c] = type_lot
                else :
                    liste_copros['lot_autre'][row_c] = type_lot

    df = pd.DataFrame(liste_copros)
    #print (fichier)
    df.to_csv('tests/liste_coproprietaires.csv', sep=';', index=False)
    return 'tests/liste_coproprietaires.csv'




fichier = pd.read_csv("tests/liste_coproprietaires.csv", delimiter=';', encoding='latin-1')
#elle me retourne le nom du fichier  
new_list = transform_file(fichier) # on veut comprendre pour il met dans ville que mer 

liste_lot = pd.read_csv("tests/liste_lots.csv", delimiter=';', encoding='latin-1')
#retourne le nom du fichier liste_lots qui a été mis à jour 
fichier_lot = tri_liste_lot(liste_lot)

#on vient faire la comparaison
new_list = add_lot(fichier_lot, new_list)

