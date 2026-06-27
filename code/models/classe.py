"""Classe Classe : un groupe d'élèves (ex. 3ème A). Agrège des Eleve."""

from __future__ import annotations
from typing import List
from .eleve import Eleve


class Classe:
    """Représente une classe scolaire.

    Relation d'agrégation avec Eleve : une Classe regroupe des élèves,
    mais un Eleve continue d'exister indépendamment de sa Classe.
    """

    def __init__(self, nom: str, niveau: str):
        self.nom = nom
        self.niveau = niveau
        self._eleves: List[Eleve] = []

    @property
    def nom(self) -> str:
        return self._nom

    @nom.setter
    def nom(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le nom de la classe ne peut pas être vide.")
        self._nom = valeur.strip()

    @property
    def niveau(self) -> str:
        return self._niveau

    @niveau.setter
    def niveau(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le niveau ne peut pas être vide.")
        self._niveau = valeur.strip()

    @property
    def eleves(self) -> List[Eleve]:
        return list(self._eleves)

    @property
    def effectif(self) -> int:
        return len(self._eleves)

    def ajouter_eleve(self, eleve: Eleve) -> None:
        if not isinstance(eleve, Eleve):
            raise TypeError("Seul un Eleve peut être ajouté à une Classe.")
        if eleve in self._eleves:
            raise ValueError(f"{eleve.nom_complet()} est déjà dans la classe {self.nom}.")
        self._eleves.append(eleve)
        eleve.classe = self

    def retirer_eleve(self, eleve: Eleve) -> None:
        if eleve not in self._eleves:
            raise ValueError(f"{eleve.nom_complet()} n'appartient pas à la classe {self.nom}.")
        self._eleves.remove(eleve)
        eleve.classe = None

    def __str__(self) -> str:
        return f"{self.nom} ({self.effectif} élève(s))"

    def __repr__(self) -> str:
        return f"Classe({self.nom!r}, niveau={self.niveau!r}, effectif={self.effectif})"
