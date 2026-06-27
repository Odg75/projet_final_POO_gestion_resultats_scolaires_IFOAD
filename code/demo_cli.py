#!/usr/bin/env python3
"""Démonstration en ligne de commande (sans interface graphique).

Exerce l'ensemble des couches (modèles, services) sur le jeu de données
de démonstration : utile pour vérifier rapidement que tout fonctionne,
sans avoir besoin d'un environnement graphique.

Usage : python demo_cli.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from services import (
    AuthService, AnalyseurStatistique, GenerateurBulletin,
    creer_jeu_de_donnees_demo, ErreurAuthentification,
)


def ligne(titre: str) -> None:
    print(f"\n=== {titre} ===")


def main() -> None:
    gr = creer_jeu_de_donnees_demo()
    classe = gr.trouver_classe("3ème A")
    auth = AuthService(gr.utilisateurs)
    analyseur = AnalyseurStatistique(gr.annee_scolaire)
    generateur = GenerateurBulletin(gr.annee_scolaire)

    ligne("Authentification")
    admin = auth.authentifier("secretariat", "admin1234")
    print(f"Connexion réussie : {admin}")
    try:
        auth.authentifier("secretariat", "mauvais_mdp")
    except ErreurAuthentification as exc:
        print(f"Rejet attendu : {exc}")

    enseignant_user = auth.authentifier("konate", "prof1234")
    print(f"Droits de {enseignant_user} sur 3ème A / Mathématiques :",
          auth.peut_saisir_notes(enseignant_user, classe, gr.trouver_matiere("Mathématiques")))
    print(f"Droits de {enseignant_user} sur 3ème A / Français :",
          auth.peut_saisir_notes(enseignant_user, classe, gr.trouver_matiere("Français")))

    ligne("Classement - Trimestre 2 - 3ème A")
    for rang, eleve, moyenne in analyseur.classement(classe, 2):
        print(f"  {rang}. {eleve.nom_complet():<22} {moyenne:>5.2f} / 20")

    ligne("Statistiques de classe - Trimestre 2")
    print("Moyenne de la classe :", analyseur.moyenne_classe(classe, 2))
    print("Répartition des mentions :", analyseur.repartition_mentions(classe, 2))
    print("Taux de réussite annuel (sur les moyennes disponibles) :", analyseur.taux_reussite_annuel(classe))

    ligne("Bulletin du 2e trimestre - Diallo Aïcha")
    bulletin_t2 = generateur.generer(classe.eleves[0], classe, 2)
    for ligne_bulletin in bulletin_t2.lignes:
        print(f"  {ligne_bulletin.matiere_nom:<15} coef {ligne_bulletin.coefficient:<3g} -> {ligne_bulletin.moyenne:.2f}/20")
    print(f"  Moyenne du trimestre : {bulletin_t2.moyenne_trimestre}/20 - Rang {bulletin_t2.rang_trimestre} - Mention {bulletin_t2.mention_trimestre}")

    ligne("Bulletin du 3e trimestre (avec résultats annuels) - Diallo Aïcha")
    bulletin_t3 = generateur.generer(classe.eleves[0], classe, 3)
    print(f"  Moyenne T3 : {bulletin_t3.moyenne_trimestre}/20 - Rang {bulletin_t3.rang_trimestre} - Mention {bulletin_t3.mention_trimestre}")
    print(f"  Moyenne annuelle : {bulletin_t3.moyenne_annuelle}/20 - Rang annuel {bulletin_t3.rang_annuel} - Mention {bulletin_t3.mention_annuelle}")
    print(f"  Décision : {bulletin_t3.decision_passage}")

    ligne("Validation des notes")
    nb = gr.valider_notes(classe, gr.trouver_matiere("Français"), 1)
    print(f"{nb} note(s) de Français validée(s) pour le trimestre 1.")

    print("\nDémonstration terminée avec succès.")


if __name__ == "__main__":
    main()
