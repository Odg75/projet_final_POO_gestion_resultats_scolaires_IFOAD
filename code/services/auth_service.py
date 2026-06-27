"""Service d'authentification et de contrôle des droits d'accès."""

from __future__ import annotations
from typing import List
from models import Utilisateur, RoleUtilisateur, Classe, Matiere


class ErreurAuthentification(Exception):
    """Levée quand l'identifiant ou le mot de passe est incorrect."""


class AuthService:
    """Gère la connexion et les permissions selon le rôle de l'utilisateur.

    - Administrateur (Directeur / Secrétariat) : accès complet.
    - Enseignant : limité à ses classes affectées et sa/ses matière(s).
    """

    def __init__(self, utilisateurs: List[Utilisateur]):
        self._utilisateurs = utilisateurs

    def authentifier(self, identifiant: str, mot_de_passe: str) -> Utilisateur:
        identifiant_normalise = (identifiant or "").strip().lower()
        for utilisateur in self._utilisateurs:
            if utilisateur.identifiant == identifiant_normalise:
                if not utilisateur.actif:
                    raise ErreurAuthentification("Ce compte a été désactivé.")
                if utilisateur.verifier_mot_de_passe(mot_de_passe):
                    return utilisateur
                raise ErreurAuthentification("Mot de passe incorrect.")
        raise ErreurAuthentification("Identifiant inconnu.")

    @staticmethod
    def peut_administrer(utilisateur: Utilisateur) -> bool:
        return utilisateur.role is RoleUtilisateur.ADMINISTRATEUR

    @staticmethod
    def peut_valider_notes(utilisateur: Utilisateur) -> bool:
        """Seul l'Administrateur (Directeur/Secrétariat) valide et verrouille les notes."""
        return utilisateur.role is RoleUtilisateur.ADMINISTRATEUR

    @staticmethod
    def peut_saisir_notes(utilisateur: Utilisateur, classe: Classe, matiere: Matiere) -> bool:
        if utilisateur.role is RoleUtilisateur.ADMINISTRATEUR:
            return True
        if utilisateur.enseignant is None:
            return False
        return utilisateur.enseignant.enseigne_a(classe, matiere)

    @staticmethod
    def classes_visibles(utilisateur: Utilisateur, toutes_les_classes: List[Classe]) -> List[Classe]:
        if utilisateur.role is RoleUtilisateur.ADMINISTRATEUR:
            return list(toutes_les_classes)
        if utilisateur.enseignant is None:
            return []
        return utilisateur.enseignant.classes_affectees()
