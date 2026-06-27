"""Classe Trimestre : compose les notes saisies durant la période."""

from __future__ import annotations
from typing import List
from .note import Note
from .eleve import Eleve


class Trimestre:
    """Un trimestre (1, 2 ou 3) d'une année scolaire.

    Relation de composition avec Note : les notes d'un trimestre n'ont pas
    de sens hors de ce trimestre (elles sont créées et détruites avec lui).
    """

    def __init__(self, numero: int):
        if numero not in (1, 2, 3):
            raise ValueError("Le numéro du trimestre doit être 1, 2 ou 3.")
        self.numero = numero
        self._notes: List[Note] = []

    @property
    def notes(self) -> List[Note]:
        return list(self._notes)

    def ajouter_note(self, note: Note) -> None:
        if not isinstance(note, Note):
            raise TypeError("Seule une Note peut être ajoutée à un Trimestre.")
        if note.trimestre_numero != self.numero:
            raise ValueError("Le trimestre de la note ne correspond pas à ce Trimestre.")
        self._notes.append(note)

    def notes_de(self, eleve: Eleve) -> List[Note]:
        return [n for n in self._notes if n.eleve == eleve]

    def moyenne_eleve(self, eleve: Eleve) -> float | None:
        """Moyenne pondérée par le coefficient de chaque matière. None si aucune note."""
        notes = self.notes_de(eleve)
        if not notes:
            return None
        total_points = sum(n.valeur * n.matiere.coefficient for n in notes)
        total_coef = sum(n.matiere.coefficient for n in notes)
        if total_coef == 0:
            return None
        return round(total_points / total_coef, 2)

    def toutes_notes_validees(self, eleve: Eleve | None = None) -> bool:
        notes = self.notes_de(eleve) if eleve else self._notes
        return all(n.statut.value == "Validée" for n in notes) if notes else False

    def __str__(self) -> str:
        return f"Trimestre {self.numero} ({len(self._notes)} note(s))"

    def __repr__(self) -> str:
        return f"Trimestre(numero={self.numero}, nb_notes={len(self._notes)})"
