"""Classe de base Personne : socle commun à Eleve et Enseignant (héritage)."""

from __future__ import annotations
from datetime import date


class Personne:
    """Représente une personne physique de l'établissement.

    Classe de base destinée à être héritée par Eleve et Enseignant.
    Toutes les données sont encapsulées : accès uniquement via propriétés,
    avec validation dans les setters.
    """

    SEXES_VALIDES = ("M", "F")

    def __init__(self, nom: str, prenom: str, date_naissance: date, sexe: str):
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance
        self.sexe = sexe

    # --- nom ---
    @property
    def nom(self) -> str:
        return self._nom

    @nom.setter
    def nom(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le nom ne peut pas être vide.")
        self._nom = valeur.strip().upper()

    # --- prenom ---
    @property
    def prenom(self) -> str:
        return self._prenom

    @prenom.setter
    def prenom(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le prénom ne peut pas être vide.")
        self._prenom = valeur.strip().title()

    # --- date_naissance ---
    @property
    def date_naissance(self) -> date:
        return self._date_naissance

    @date_naissance.setter
    def date_naissance(self, valeur: date) -> None:
        if not isinstance(valeur, date):
            raise TypeError("La date de naissance doit être un objet date.")
        if valeur >= date.today():
            raise ValueError("La date de naissance doit être dans le passé.")
        self._date_naissance = valeur

    # --- sexe ---
    @property
    def sexe(self) -> str:
        return self._sexe

    @sexe.setter
    def sexe(self, valeur: str) -> None:
        valeur = (valeur or "").strip().upper()
        if valeur not in self.SEXES_VALIDES:
            raise ValueError(f"Sexe invalide : doit être {self.SEXES_VALIDES}.")
        self._sexe = valeur

    def nom_complet(self) -> str:
        return f"{self.nom} {self.prenom}"

    def age(self, a_la_date: date | None = None) -> int:
        reference = a_la_date or date.today()
        annees = reference.year - self.date_naissance.year
        if (reference.month, reference.day) < (self.date_naissance.month, self.date_naissance.day):
            annees -= 1
        return annees

    def __str__(self) -> str:
        return self.nom_complet()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.nom_complet()!r})"
