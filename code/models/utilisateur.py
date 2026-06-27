"""Classe Utilisateur : compte de connexion (Administrateur ou Enseignant)."""

from __future__ import annotations
import hashlib
from enum import Enum
from typing import Optional
from .enseignant import Enseignant


class RoleUtilisateur(Enum):
    ADMINISTRATEUR = "Administrateur"  # Directeur ou Secrétariat : accès complet
    ENSEIGNANT = "Enseignant"          # Accès restreint à ses classes/matières


class Utilisateur:
    """Compte permettant de se connecter à l'application.

    - Un compte Administrateur n'est lié à aucun Enseignant (accès complet).
    - Un compte Enseignant est associé à exactement un Enseignant (association
      Utilisateur <-> Enseignant), dont il hérite les droits restreints.
    """

    def __init__(self, identifiant: str, mot_de_passe: str, role: RoleUtilisateur,
                 enseignant: Optional[Enseignant] = None):
        self.identifiant = identifiant
        self.role = role
        self.enseignant = enseignant
        self._mot_de_passe_hash = self._hacher(mot_de_passe)
        self.actif = True

    @property
    def identifiant(self) -> str:
        return self._identifiant

    @identifiant.setter
    def identifiant(self, valeur: str) -> None:
        if not valeur or not valeur.strip():
            raise ValueError("L'identifiant ne peut pas être vide.")
        self._identifiant = valeur.strip().lower()

    @property
    def role(self) -> RoleUtilisateur:
        return self._role

    @role.setter
    def role(self, valeur: RoleUtilisateur) -> None:
        if not isinstance(valeur, RoleUtilisateur):
            raise TypeError("role doit être une valeur de RoleUtilisateur.")
        self._role = valeur

    @property
    def enseignant(self) -> Optional[Enseignant]:
        return self._enseignant

    @enseignant.setter
    def enseignant(self, valeur: Optional[Enseignant]) -> None:
        if valeur is not None and not isinstance(valeur, Enseignant):
            raise TypeError("enseignant doit être une instance de Enseignant ou None.")
        self._enseignant = valeur

    @staticmethod
    def _hacher(mot_de_passe: str) -> str:
        if not mot_de_passe or len(mot_de_passe) < 4:
            raise ValueError("Le mot de passe doit contenir au moins 4 caractères.")
        return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()

    def verifier_mot_de_passe(self, mot_de_passe: str) -> bool:
        return self._hacher_verif(mot_de_passe) == self._mot_de_passe_hash

    def _hacher_verif(self, mot_de_passe: str) -> str:
        return hashlib.sha256(mot_de_passe.encode("utf-8")).hexdigest()

    def changer_mot_de_passe(self, nouveau_mot_de_passe: str) -> None:
        self._mot_de_passe_hash = self._hacher(nouveau_mot_de_passe)

    def est_administrateur(self) -> bool:
        return self.role is RoleUtilisateur.ADMINISTRATEUR

    def __str__(self) -> str:
        return f"{self.identifiant} ({self.role.value})"

    def __repr__(self) -> str:
        return f"Utilisateur({self.identifiant!r}, role={self.role.value!r})"
