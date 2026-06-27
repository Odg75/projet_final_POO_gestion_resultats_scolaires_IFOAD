#!/usr/bin/env python3
"""Point d'entrée de l'application graphique.

Charge les données sauvegardées (data/donnees.pkl) si elles existent,
sinon démarre avec un jeu de données de démonstration.
"""

import sys
from pathlib import Path

# Permet de lancer "python main.py" depuis n'importe quel dossier.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services import GestionnaireResultats, creer_jeu_de_donnees_demo
from gui.app import Application

CHEMIN_DONNEES = Path(__file__).resolve().parent / "data" / "donnees.pkl"


def charger_ou_creer_gestionnaire() -> GestionnaireResultats:
    if CHEMIN_DONNEES.exists():
        try:
            return GestionnaireResultats.charger(CHEMIN_DONNEES)
        except Exception as exc:
            print(f"Impossible de charger {CHEMIN_DONNEES} ({exc}). Démarrage avec des données de démonstration.")
    return creer_jeu_de_donnees_demo()


def main() -> None:
    gestionnaire = charger_ou_creer_gestionnaire()
    application = Application(gestionnaire)

    def quitter() -> None:
        gestionnaire.sauvegarder(CHEMIN_DONNEES)
        application.destroy()

    application.protocol("WM_DELETE_WINDOW", quitter)
    application.mainloop()


if __name__ == "__main__":
    main()
