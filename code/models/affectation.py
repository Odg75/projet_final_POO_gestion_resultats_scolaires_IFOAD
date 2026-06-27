"""Classe Affectation : association ternaire Enseignant - Classe - Matiere."""

from __future__ import annotations
from .enseignant import Enseignant
from .classe import Classe
from .matiere import Matiere


class Affectation:
    """Représente le fait qu'un Enseignant enseigne une Matiere à une Classe.

    Un même enseignant peut avoir plusieurs Affectation (plusieurs classes
    et/ou plusieurs matières).
    """

    def __init__(self, enseignant: Enseignant, classe: Classe, matiere: Matiere):
        if not isinstance(enseignant, Enseignant):
            raise TypeError("enseignant doit être une instance de Enseignant.")
        if not isinstance(classe, Classe):
            raise TypeError("classe doit être une instance de Classe.")
        if not isinstance(matiere, Matiere):
            raise TypeError("matiere doit être une instance de Matiere.")
        self.enseignant = enseignant
        self.classe = classe
        self.matiere = matiere

    def __eq__(self, autre: object) -> bool:
        return (
            isinstance(autre, Affectation)
            and self.enseignant == autre.enseignant
            and self.classe == autre.classe
            and self.matiere == autre.matiere
        )

    def __hash__(self) -> int:
        return hash((self.enseignant, self.classe, self.matiere))

    def __str__(self) -> str:
        return f"{self.enseignant.nom_complet()} -> {self.matiere.nom} en {self.classe.nom}"

    def __repr__(self) -> str:
        return f"Affectation({self.enseignant!r}, {self.classe!r}, {self.matiere!r})"
