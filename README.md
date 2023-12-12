# liste-corpopri-taire
Récupérer les
=> il y a des beugs sur les adresses et villes de liste_copropriétaire sur le ytrès grand échantillons sur les lignes 14 - 15 - 41 - 35 - 61 - 68 - 127 - 128 - 193 - 195 - 209 - 399 - 332
=> j'ai du remettre le / pour séparé les coordonnées car il y en a entre les coordonnées dans le fichier de base de ICS, je ne sais plus vraiment pourquoi je l'avais supprimé par un ! mais je pense que c'est pour éviter les erreurs sur des informations transmises qui peuvent être des dates. 
=> indiquer que si on met des copropriété dans notre fichier user qu'il n'y a pas dans liste ics on en tiendra pas compte, à l'inverse il rajoutera les copropriété présente dans liste ics et non présente dans liste user. 
=> problème sur les lignes tel et informations voici ce que j'ai sur informations : Tel. / 02 23 52 16 46 Tel. 
Tel fixe / 06 77 47 69 35 Tel portable 
=> protéger la fiche nottament colone numéro de copro et numéro copropriétaire pour la MAJ. 
=> ajouter du vert quand nouveau proprio et ajouter du vert sur les proprio qui ont changés d'info. 
=> regler ce problème qui fait que si un numéro se trouve dans le nom de la copro alors il va le mettre dans le numéro de la copro exemple : 401446	MOKA 
=> dès que l'app se coupe elle supprime les fichiers CSV présents 
=> au lieu de supprimer un par un tous les csv juste faire une boucle qui supprime tous les csv, dans /MAJliste supprimer tous sauf liste_copropriétaires.csv 
=> Tester avec plusieurs copro si RP OUI/NON marche bien et lot OUI/NON marche bien,
=> intégrer une vidéo explicative du rendu finale et de comment récupérer ses fichiers sur ICS et changer les images actuellement affiché. 
=> S'il y a un beug sur une ligne au lieu de faire une erreur, il renvoie le beug de la ligne avec les informations récupérées à l'user qui l'enregistre manuellement. 
=> regarder si je peux créer un fichier qui éxécute du code dans le terminal afin de lancer mon programme et ainsi faire tout en local sur les ordi et ne pas avoir besoin de push en ligne mon code. 
=> faire un système de connexions pour une entreprise.
=> faire mon truc de clé en extractant de ICS les entreprises et copropriétaire (pour noter qui récupère les clés ou pour des clés stocké chez nous de clés privative) QUID des nouvelles entreprises ou coprorpriétaire qui ne serait pas dans la liste à jour ? 


