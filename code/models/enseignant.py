"""Classe Enseignant : hérite de Personne. Lié à ses Affectation (classe+matière)."""

from __future__ import annotations
from datetime import date
import itertools
from typing import List, TYPE_CHECKING
from .personne import Personne

if TYPE_CHECKING:
    from .affectation import Affectation


class Enseignant(Personne):
    """Un enseignant. Hérite de Personne.

    Un enseignant peut avoir plusieurs Affectation (plusieurs classes ET
    plusieurs matières) : la liste est gérée ici par composition légère
    (l'Affectation n'a pas de sens sans l'enseignant qu'elle référence),
    mais retirée proprement via retirer_affectation.
    """

    _compteur = itertools.count(1)

    def __init__(self, nom: str, prenom: str, date_naissance: date, sexe: str,
                 specialite: str = "", code: str | None = None):
        super().__init__(nom, prenom, date_naissance, sexe)
        self.specialite = specialite
        self.code = code or f"ENS{next(self._compteur):04d}"
        self._affectations: List["Affectation"] = []

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("Le code enseignant ne peut pas être vide.")
        self._code = valeur.strip()

    @property
    def affectations(self) -> List["Affectation"]:
        return list(self._affectations)

    def ajouter_affectation(self, affectation: "Affectation") -> None:
        if affectation in self._affectations:
            raise ValueError("Cette affectation existe déjà pour cet enseignant.")
        self._affectations.append(affectation)

    def retirer_affectation(self, affectation: "Affectation") -> None:
        if affectation not in self._affectations:
            raise ValueError("Affectation introuvable pour cet enseignant.")
        self._affectations.remove(affectation)

    def classes_affectees(self) -> List:
        return list({a.classe for a in self._affectations})

    def matieres_enseignees(self) -> List:
        return list({a.matiere for a in self._affectations})

    def enseigne_a(self, classe, matiere) -> bool:
        return any(a.classe == classe and a.matiere == matiere for a in self._affectations)

    def __eq__(self, autre: object) -> bool:
        return isinstance(autre, Enseignant) and self.code == autre.code

    def __hash__(self) -> int:
        return hash(self.code)

    def __str__(self) -> str:
        return f"{self.nom_complet()} ({self.specialite or 'enseignant'})"

    def __repr__(self) -> str:
        return f"Enseignant({self.nom_complet()!r}, code={self.code!r})"
