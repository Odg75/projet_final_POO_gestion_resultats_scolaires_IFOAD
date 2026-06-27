"""Jeu de données de démonstration : utilisé par main.py et demo_cli.py
pour ne pas démarrer sur une application totalement vide."""

from __future__ import annotations
import datetime
from models import Eleve, Enseignant, Matiere, Classe
from .gestionnaire_resultats import GestionnaireResultats


def creer_jeu_de_donnees_demo() -> GestionnaireResultats:
    gr = GestionnaireResultats(annee_scolaire=None)  # AnneeScolaire("2025-2026") par défaut

    classe_3a = Classe("3ème A", "3ème")
    classe_2a = Classe("2nde A", "2nde")
    gr.ajouter_classe(classe_3a)
    gr.ajouter_classe(classe_2a)

    maths = Matiere("Mathématiques", 4)
    francais = Matiere("Français", 3)
    anglais = Matiere("Anglais", 2)
    svt = Matiere("SVT", 2)
    for matiere in (maths, francais, anglais, svt):
        gr.ajouter_matiere(matiere)

    eleves_3a = [
        Eleve("Diallo", "Aïcha", datetime.date(2010, 3, 4), "F"),
        Eleve("Traoré", "Ismaël", datetime.date(2010, 7, 1), "M"),
        Eleve("Sankara", "Aminata", datetime.date(2010, 2, 2), "F"),
        Eleve("Ouattara", "Boukary", datetime.date(2010, 5, 12), "M"),
        Eleve("Kaboré", "Fatim", datetime.date(2010, 9, 21), "F"),
    ]
    for eleve in eleves_3a:
        gr.ajouter_eleve(eleve, classe_3a)

    eleves_2a = [
        Eleve("Nikiema", "Boris", datetime.date(2011, 4, 18), "M"),
        Eleve("Zongo", "Awa", datetime.date(2011, 1, 9), "F"),
    ]
    for eleve in eleves_2a:
        gr.ajouter_eleve(eleve, classe_2a)

    prof_maths = Enseignant("Konaté", "Sékou", datetime.date(1985, 1, 1), "M", specialite="Mathématiques")
    prof_lettres = Enseignant("Sawadogo", "Rasmata", datetime.date(1988, 6, 15), "F", specialite="Français-Anglais")
    for enseignant in (prof_maths, prof_lettres):
        gr.ajouter_enseignant(enseignant)

    gr.affecter(prof_maths, classe_3a, maths)
    gr.affecter(prof_maths, classe_2a, maths)
    gr.affecter(prof_lettres, classe_3a, francais)
    gr.affecter(prof_lettres, classe_3a, anglais)

    gr.creer_compte_administrateur("secretariat", "admin1234")
    gr.creer_compte_enseignant("konate", "prof1234", prof_maths)
    gr.creer_compte_enseignant("sawadogo", "prof1234", prof_lettres)

    notes_3a = {
        eleves_3a[0]: {maths: [15, 16, 14], francais: [12, 11, 13], anglais: [14, 15, 13], svt: [11, 12, 10]},
        eleves_3a[1]: {maths: [8, 9, 7], francais: [10, 9, 11], anglais: [11, 10, 12], svt: [9, 8, 10]},
        eleves_3a[2]: {maths: [18, 19, 17], francais: [16, 15, 17], anglais: [17, 18, 16], svt: [15, 16, 15]},
        eleves_3a[3]: {maths: [12, 13, 11], francais: [13, 12, 12], anglais: [12, 13, 11], svt: [10, 11, 12]},
        eleves_3a[4]: {maths: [14, 13, 15], francais: [15, 14, 15], anglais: [13, 14, 14], svt: [12, 13, 13]},
    }
    for trimestre_numero in (1, 2, 3):
        for eleve, par_matiere in notes_3a.items():
            for matiere, valeurs in par_matiere.items():
                gr.saisir_note(eleve, matiere, trimestre_numero, valeurs[trimestre_numero - 1])

    gr.valider_notes(classe_3a, maths, 1)
    gr.valider_notes(classe_3a, maths, 2)

    return gr
