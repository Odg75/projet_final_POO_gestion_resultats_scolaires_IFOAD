"""Classe AnneeScolaire : agrège les 3 Trimestre de l'année."""

from __future__ import annotations
from typing import List, Optional
from .trimestre import Trimestre
from .eleve import Eleve


class AnneeScolaire:
    """Une année scolaire (ex. "2025-2026"), composée de 3 trimestres.

    Relation d'agrégation : les Trimestre sont créés directement par
    l'AnneeScolaire à l'initialisation (1 à 3), elle en porte la responsabilité.
    """

    SEUIL_PASSAGE = 10.0  # moyenne annuelle minimale pour passer en classe supérieure

    def __init__(self, libelle: str):
        if not libelle or not libelle.strip():
            raise ValueError("Le libellé de l'année scolaire ne peut pas être vide.")
        self.libelle = libelle.strip()
        self._trimestres: List[Trimestre] = [Trimestre(i) for i in (1, 2, 3)]

    @property
    def trimestres(self) -> List[Trimestre]:
        return list(self._trimestres)

    def trimestre(self, numero: int) -> Trimestre:
        if numero not in (1, 2, 3):
            raise ValueError("Le numéro du trimestre doit être 1, 2 ou 3.")
        return self._trimestres[numero - 1]

    def moyenne_annuelle(self, eleve: Eleve) -> Optional[float]:
        """Moyenne simple des 3 moyennes trimestrielles disponibles."""
        moyennes = [t.moyenne_eleve(eleve) for t in self._trimestres]
        moyennes = [m for m in moyennes if m is not None]
        if not moyennes:
            return None
        return round(sum(moyennes) / len(moyennes), 2)

    def decision_passage(self, eleve: Eleve) -> Optional[str]:
        moyenne = self.moyenne_annuelle(eleve)
        if moyenne is None:
            return None
        return "Admis(e) en classe supérieure" if moyenne >= self.SEUIL_PASSAGE else "Doit redoubler"

    def __str__(self) -> str:
        return f"Année scolaire {self.libelle}"

    def __repr__(self) -> str:
        return f"AnneeScolaire({self.libelle!r})"
