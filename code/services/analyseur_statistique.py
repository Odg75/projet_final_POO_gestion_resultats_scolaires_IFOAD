"""Service d'analyse statistique : moyennes, classements, mentions, taux de réussite."""

from __future__ import annotations
from typing import List, Optional, Tuple
from models import Classe, Matiere, AnneeScolaire, Eleve

SEUILS_MENTIONS = (
    (16.0, "Très bien"),
    (14.0, "Bien"),
    (12.0, "Assez bien"),
    (10.0, "Passable"),
    (0.0, "Insuffisant"),
)


class AnalyseurStatistique:
    """Calcule les indicateurs statistiques à partir de l'AnneeScolaire."""

    def __init__(self, annee_scolaire: AnneeScolaire):
        self.annee_scolaire = annee_scolaire

    @staticmethod
    def mention(moyenne: Optional[float]) -> Optional[str]:
        if moyenne is None:
            return None
        for seuil, libelle in SEUILS_MENTIONS:
            if moyenne >= seuil:
                return libelle
        return SEUILS_MENTIONS[-1][1]

    def classement(self, classe: Classe, trimestre_numero: int) -> List[Tuple[int, Eleve, float]]:
        """Liste (rang, élève, moyenne) triée par moyenne décroissante, ex-aequo gérés."""
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        resultats = []
        for eleve in classe.eleves:
            moyenne = trimestre.moyenne_eleve(eleve)
            if moyenne is not None:
                resultats.append((eleve, moyenne))
        resultats.sort(key=lambda couple: couple[1], reverse=True)

        classement: List[Tuple[int, Eleve, float]] = []
        rang_courant = 0
        moyenne_precedente = None
        for index, (eleve, moyenne) in enumerate(resultats, start=1):
            if moyenne != moyenne_precedente:
                rang_courant = index
                moyenne_precedente = moyenne
            classement.append((rang_courant, eleve, moyenne))
        return classement

    def rang_eleve(self, classe: Classe, eleve: Eleve, trimestre_numero: int) -> Optional[int]:
        for rang, eleve_classe, _ in self.classement(classe, trimestre_numero):
            if eleve_classe == eleve:
                return rang
        return None

    def classement_annuel(self, classe: Classe) -> List[Tuple[int, Eleve, float]]:
        resultats = []
        for eleve in classe.eleves:
            moyenne = self.annee_scolaire.moyenne_annuelle(eleve)
            if moyenne is not None:
                resultats.append((eleve, moyenne))
        resultats.sort(key=lambda couple: couple[1], reverse=True)

        classement: List[Tuple[int, Eleve, float]] = []
        rang_courant = 0
        moyenne_precedente = None
        for index, (eleve, moyenne) in enumerate(resultats, start=1):
            if moyenne != moyenne_precedente:
                rang_courant = index
                moyenne_precedente = moyenne
            classement.append((rang_courant, eleve, moyenne))
        return classement

    def moyenne_classe(self, classe: Classe, trimestre_numero: int) -> Optional[float]:
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        moyennes = [trimestre.moyenne_eleve(e) for e in classe.eleves]
        moyennes = [m for m in moyennes if m is not None]
        return round(sum(moyennes) / len(moyennes), 2) if moyennes else None

    def moyenne_matiere(self, classe: Classe, matiere: Matiere, trimestre_numero: int) -> Optional[float]:
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        notes = [n for n in trimestre.notes if n.matiere == matiere and n.eleve.classe == classe]
        if not notes:
            return None
        return round(sum(n.valeur for n in notes) / len(notes), 2)

    def repartition_mentions(self, classe: Classe, trimestre_numero: int) -> dict:
        repartition = {libelle: 0 for _, libelle in SEUILS_MENTIONS}
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        for eleve in classe.eleves:
            moyenne = trimestre.moyenne_eleve(eleve)
            mention = self.mention(moyenne)
            if mention:
                repartition[mention] += 1
        return repartition

    def taux_reussite_annuel(self, classe: Classe) -> Optional[float]:
        decisions = [self.annee_scolaire.decision_passage(e) for e in classe.eleves]
        decisions = [d for d in decisions if d is not None]
        if not decisions:
            return None
        admis = sum(1 for d in decisions if d.startswith("Admis"))
        return round(100 * admis / len(decisions), 1)

    def meilleure_moyenne(self, classe: Classe, trimestre_numero: int) -> Optional[Tuple[Eleve, float]]:
        classement = self.classement(classe, trimestre_numero)
        return (classement[0][1], classement[0][2]) if classement else None

    def plus_faible_moyenne(self, classe: Classe, trimestre_numero: int) -> Optional[Tuple[Eleve, float]]:
        classement = self.classement(classe, trimestre_numero)
        return (classement[-1][1], classement[-1][2]) if classement else None
