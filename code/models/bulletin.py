"""Classe Bulletin : composition des notes (et résultats) d'un élève."""

from __future__ import annotations
from typing import List, Optional
from .eleve import Eleve


class LigneBulletin:
    """Une ligne du bulletin : une matière, son coefficient et la moyenne obtenue."""

    def __init__(self, matiere_nom: str, coefficient: float, moyenne: float):
        self.matiere_nom = matiere_nom
        self.coefficient = coefficient
        self.moyenne = moyenne

    def __repr__(self) -> str:
        return f"LigneBulletin({self.matiere_nom!r}, coef={self.coefficient}, moyenne={self.moyenne})"


class Bulletin:
    """Bulletin d'un élève pour un trimestre donné.

    Composition : les LigneBulletin n'existent que dans le cadre de ce
    Bulletin précis (elles sont créées et détruites avec lui).
    Pour le 3e trimestre, les champs annuels (*_annuel*) sont en plus remplis.
    """

    def __init__(self, eleve: Eleve, annee_libelle: str, trimestre_numero: int):
        self.eleve = eleve
        self.annee_libelle = annee_libelle
        self.trimestre_numero = trimestre_numero
        self.lignes: List[LigneBulletin] = []
        self.moyenne_trimestre: Optional[float] = None
        self.rang_trimestre: Optional[int] = None
        self.mention_trimestre: Optional[str] = None
        # Renseignés uniquement pour le bulletin du 3e trimestre
        self.moyenne_annuelle: Optional[float] = None
        self.rang_annuel: Optional[int] = None
        self.mention_annuelle: Optional[str] = None
        self.decision_passage: Optional[str] = None

    @property
    def est_bulletin_annuel(self) -> bool:
        return self.trimestre_numero == 3

    def ajouter_ligne(self, ligne: LigneBulletin) -> None:
        self.lignes.append(ligne)

    def __str__(self) -> str:
        suffixe = " + résultats annuels" if self.est_bulletin_annuel else ""
        return f"Bulletin de {self.eleve.nom_complet()} - T{self.trimestre_numero}{suffixe}"

    def __repr__(self) -> str:
        return f"Bulletin(eleve={self.eleve.matricule!r}, T{self.trimestre_numero})"
