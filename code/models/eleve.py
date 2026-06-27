"""Classe Eleve : hérite de Personne. Association avec Classe et Note."""

from __future__ import annotations
from datetime import date
import itertools
from .personne import Personne


class Eleve(Personne):
    """Un élève. Hérite de Personne (nom, prénom, date de naissance, sexe).

    Le lien vers sa Classe est une association simple (l'élève connaît sa
    classe, et inversement, mais les deux objets ont un cycle de vie propre).
    """

    _compteur = itertools.count(1)

    def __init__(self, nom: str, prenom: str, date_naissance: date, sexe: str,
                 date_inscription: date | None = None, matricule: str | None = None):
        super().__init__(nom, prenom, date_naissance, sexe)
        self.matricule = matricule or f"EL{next(self._compteur):04d}"
        self.date_inscription = date_inscription or date.today()
        self.classe = None  # type: ignore[assignment]  # référence vers Classe, gérée par Classe

    @property
    def matricule(self) -> str:
        return self._matricule

    @matricule.setter
    def matricule(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le matricule ne peut pas être vide.")
        self._matricule = valeur.strip()

    def __eq__(self, autre: object) -> bool:
        return isinstance(autre, Eleve) and self.matricule == autre.matricule

    def __hash__(self) -> int:
        return hash(self.matricule)

    def __str__(self) -> str:
        classe = self.classe.nom if self.classe else "non affecté"
        return f"{self.nom_complet()} ({self.matricule}) - {classe}"

    def __repr__(self) -> str:
        return f"Eleve({self.nom_complet()!r}, matricule={self.matricule!r})"
