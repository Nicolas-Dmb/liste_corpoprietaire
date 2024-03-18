import os
import subprocess


dossier_actuel = os.getcwd()
commande_flask = ["flask", "run", "--host=0.0.0.0"]

# Exécution de la commande dans le terminal
subprocess.run(commande_flask, cwd=dossier_actuel)
