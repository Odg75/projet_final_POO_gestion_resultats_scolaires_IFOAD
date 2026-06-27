"""Classe Matiere : une discipline enseignée, avec son coefficient."""

from __future__ import annotations


class Matiere:
    """Représente une matière scolaire (ex. Mathématiques, coefficient 4)."""

    def __init__(self, nom: str, coefficient: float):
        self.nom = nom
        self.coefficient = coefficient

    @property
    def nom(self) -> str:
        return self._nom

    @nom.setter
    def nom(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le nom de la matière ne peut pas être vide.")
        self._nom = valeur.strip().capitalize()

    @property
    def coefficient(self) -> float:
        return self._coefficient

    @coefficient.setter
    def coefficient(self, valeur: float) -> None:
        try:
            valeur = float(valeur)
        except (TypeError, ValueError):
            raise ValueError("Le coefficient doit être un nombre.")
        if valeur <= 0:
            raise ValueError("Le coefficient doit être strictement positif.")
        self._coefficient = valeur

    def __eq__(self, autre: object) -> bool:
        return isinstance(autre, Matiere) and self.nom == autre.nom

    def __hash__(self) -> int:
        return hash(self.nom)

    def __str__(self) -> str:
        return f"{self.nom} (coef. {self.coefficient:g})"

    def __repr__(self) -> str:
        return f"Matiere({self.nom!r}, coefficient={self.coefficient!r})"
