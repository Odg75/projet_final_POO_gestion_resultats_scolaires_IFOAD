"""Package contenant les classes modèles du système de gestion des résultats scolaires."""

from .personne import Personne
from .eleve import Eleve
from .enseignant import Enseignant
from .matiere import Matiere
from .classe import Classe
from .affectation import Affectation
from .utilisateur import Utilisateur, RoleUtilisateur
from .note import Note, StatutNote
from .trimestre import Trimestre
from .annee_scolaire import AnneeScolaire
from .bulletin import Bulletin, LigneBulletin

__all__ = [
    "Personne",
    "Eleve",
    "Enseignant",
    "Matiere",
    "Classe",
    "Affectation",
    "Utilisateur",
    "RoleUtilisateur",
    "Note",
    "StatutNote",
    "Trimestre",
    "AnneeScolaire",
    "Bulletin",
    "LigneBulletin",
]
