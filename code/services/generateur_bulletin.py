"""Service de génération des bulletins (trimestriels et annuel pour le T3)."""

from __future__ import annotations
from models import Eleve, Classe, AnneeScolaire, Bulletin, LigneBulletin
from .analyseur_statistique import AnalyseurStatistique


class GenerateurBulletin:
    """Construit un Bulletin pour un élève, à partir des notes de l'année scolaire.

    Le bulletin du 3e trimestre est enrichi des résultats annuels
    (moyenne annuelle, rang annuel, mention annuelle, décision de passage).
    """

    def __init__(self, annee_scolaire: AnneeScolaire):
        self.annee_scolaire = annee_scolaire
        self.analyseur = AnalyseurStatistique(annee_scolaire)

    def generer(self, eleve: Eleve, classe: Classe, trimestre_numero: int) -> Bulletin:
        if eleve.classe != classe:
            raise ValueError(f"{eleve.nom_complet()} n'appartient pas à la classe {classe.nom}.")

        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        bulletin = Bulletin(eleve, self.annee_scolaire.libelle, trimestre_numero)

        for note in trimestre.notes_de(eleve):
            bulletin.ajouter_ligne(LigneBulletin(note.matiere.nom, note.matiere.coefficient, note.valeur))

        bulletin.moyenne_trimestre = trimestre.moyenne_eleve(eleve)
        bulletin.rang_trimestre = self.analyseur.rang_eleve(classe, eleve, trimestre_numero)
        bulletin.mention_trimestre = self.analyseur.mention(bulletin.moyenne_trimestre)

        if trimestre_numero == 3:
            bulletin.moyenne_annuelle = self.annee_scolaire.moyenne_annuelle(eleve)
            bulletin.mention_annuelle = self.analyseur.mention(bulletin.moyenne_annuelle)
            bulletin.decision_passage = self.annee_scolaire.decision_passage(eleve)
            for rang, eleve_classe, _ in self.analyseur.classement_annuel(classe):
                if eleve_classe == eleve:
                    bulletin.rang_annuel = rang
                    break

        return bulletin

    def generer_pour_classe(self, classe: Classe, trimestre_numero: int) -> list[Bulletin]:
        return [self.generer(eleve, classe, trimestre_numero) for eleve in classe.eleves]
