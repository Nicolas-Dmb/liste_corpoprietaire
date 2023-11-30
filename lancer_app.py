import os
import subprocess

# Obtenir le répertoire actuel
dossier_actuel = os.getcwd()

# Commande pour lancer Flask
commande_flask = ["flask", "run", "--host=0.0.0.0"]

# Exécution de la commande dans le terminal
subprocess.run(commande_flask, cwd=dossier_actuel)