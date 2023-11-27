# liste-corpopri-taire
Récupérer les fichiers excel d'ICS et le traiter 

=> Il faut que je fasse une page une fois que le document est renvoyé à l'user. 
=> Il faut que je fasse une selection colonne pour RP ou autre (une fois le forms fait il detecte les noms des copropriétés présente dans le fichier puis demande d'indiquer les adresses de ces copropriété, ensuite je récupère les mots clés autre que rue etc)
=> intégrer une vidéo explicative du rendu finale et de comment récupérer ses fichiers sur ICS
=> S'il y a un beug sur une ligne au lieu de faire une erreur, il renvoie le beug de la ligne avec les informations récupérées à l'user qui l'enregistre manuellement. 
=> Essayer de faire un truc qui extrait les les n° de lot uniquement des RP peut-etre pour localiser le bien dans l'immeuble 
=> Faire une deuxième algo pour faire une comparaison entre notre base excel et la base extraite de ICS et voir s'il y a eu des changements. 
=> faire un système de connexions pour une entreprise
=> faire mon truc de clé en extractant de ICS les entreprises et copropriétaire (pour noter qui récupère les clés ou pour des clés stocké chez nous de clés privative) QUID des nouvelles entreprises ou coprorpriétaire qui ne serait pas dans la liste à jour ? 
=> regarder si je peux créer un fichier qui éxécute du code dans le terminal afin de lancer mon programme et ainsi faire tout en local sur les ordi et ne pas avoir besoin de push en ligne mon code. 

j'en suis à la ligne 36 de app.py : 
- Je viens de faire le programme qui retourne pour chaque copropriétaire d'un immeuble vérifie s'il est en rp ou non. 
- ensuite dans il envoie le nouveau fichier vers l'user. 
=> sauf que la première page fonctionne mais une fois le fichier envoyé vers le serveur la deuxième page demandant à l'user les adresse ne fonctionne pas. 
[2023-11-27 17:59:33,014] ERROR in app: Exception on /fichier [POST]
Traceback (most recent call last):
  File "/usr/local/python/3.10.8/lib/python3.10/site-packages/flask/app.py", line 1455, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/python/3.10.8/lib/python3.10/site-packages/flask/app.py", line 869, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/python/3.10.8/lib/python3.10/site-packages/flask/app.py", line 867, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/python/3.10.8/lib/python3.10/site-packages/flask/app.py", line 852, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
  File "/workspaces/liste-corpopri-taire/app.py", line 39, in fichier
    liste_coproprietes = names_coproprietes(new_list)
  File "/workspaces/liste-corpopri-taire/excel.py", line 5, in names_coproprietes
    names_coproprietes.append(liste_csv[copropriete]['copropriete'])
TypeError: string indices must be integers