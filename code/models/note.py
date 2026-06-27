"""Classe Note : une note d'un élève dans une matière, pour un trimestre."""

from __future__ import annotations
from enum import Enum
from .eleve import Eleve
from .matiere import Matiere


class StatutNote(Enum):
    BROUILLON = "Brouillon"  # saisie par l'enseignant, encore modifiable
    VALIDEE = "Validée"      # verrouillée par l'Administrateur (Directeur/Secrétariat)


class Note:
    """Une note /20 attribuée à un Eleve, dans une Matiere, pour un trimestre.

    Workflow de validation : une note Brouillon peut être modifiée par
    l'enseignant. Une fois Validée par l'Administrateur, elle est verrouillée ;
    seul l'Administrateur peut encore la modifier (cf. AuthService côté service).
    """

    VALEUR_MIN = 0.0
    VALEUR_MAX = 20.0

    def __init__(self, eleve: Eleve, matiere: Matiere, trimestre_numero: int, valeur: float):
        if not isinstance(eleve, Eleve):
            raise TypeError("eleve doit être une instance de Eleve.")
        if not isinstance(matiere, Matiere):
            raise TypeError("matiere doit être une instance de Matiere.")
        if trimestre_numero not in (1, 2, 3):
            raise ValueError("trimestre_numero doit être 1, 2 ou 3.")
        self.eleve = eleve
        self.matiere = matiere
        self.trimestre_numero = trimestre_numero
        self.valeur = valeur
        self.statut = StatutNote.BROUILLON

    @property
    def valeur(self) -> float:
        return self._valeur

    @valeur.setter
    def valeur(self, valeur: float) -> None:
        try:
            valeur = float(valeur)
        except (TypeError, ValueError):
            raise ValueError("La note doit être un nombre.")
        if not (self.VALEUR_MIN <= valeur <= self.VALEUR_MAX):
            raise ValueError(f"La note doit être comprise entre {self.VALEUR_MIN} et {self.VALEUR_MAX}.")
        self._valeur = round(valeur, 2)

    def est_modifiable(self) -> bool:
        return self.statut is StatutNote.BROUILLON

    def modifier(self, nouvelle_valeur: float, forcer: bool = False) -> None:
        """Modifie la note. `forcer=True` réservé à l'Administrateur sur une note validée."""
        if not self.est_modifiable() and not forcer:
            raise PermissionError("Note validée : seul l'Administrateur peut la modifier.")
        self.valeur = nouvelle_valeur

    def valider(self) -> None:
        self.statut = StatutNote.VALIDEE

    def devalider(self) -> None:
        self.statut = StatutNote.BROUILLON

    def __str__(self) -> str:
        return f"{self.eleve.nom_complet()} - {self.matiere.nom} T{self.trimestre_numero}: {self.valeur}/20 ({self.statut.value})"

    def __repr__(self) -> str:
        return f"Note(eleve={self.eleve.matricule!r}, matiere={self.matiere.nom!r}, T{self.trimestre_numero}, valeur={self.valeur})"
