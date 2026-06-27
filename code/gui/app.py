"""Fenêtre principale de l'application : gère la navigation entre écrans."""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from models import RoleUtilisateur
from services import GestionnaireResultats, AuthService, AnalyseurStatistique, GenerateurBulletin
from .login_frame import LoginFrame
from .admin_frame import AdminFrame
from .teacher_frame import TeacherFrame


class Application(tk.Tk):
    """Fenêtre racine : affiche soit l'écran de connexion, soit le tableau
    de bord correspondant au rôle de l'utilisateur connecté."""

    def __init__(self, gestionnaire: GestionnaireResultats):
        super().__init__()
        self.title("Gestion des résultats scolaires")
        self.geometry("1000x640")
        self.minsize(820, 560)

        self.gestionnaire = gestionnaire
        self.auth_service = AuthService(gestionnaire.utilisateurs)
        self.analyseur_statistique = AnalyseurStatistique(gestionnaire.annee_scolaire)
        self.generateur_bulletin = GenerateurBulletin(gestionnaire.annee_scolaire)

        self.utilisateur_courant = None
        self._frame_courante: ttk.Frame | None = None

        self._afficher_connexion()

    # ------------------------------------------------------------------ #
    def _vider(self) -> None:
        if self._frame_courante is not None:
            self._frame_courante.destroy()
            self._frame_courante = None

    def _afficher_connexion(self) -> None:
        self._vider()
        self._frame_courante = LoginFrame(self, self)
        self._frame_courante.pack(fill="both", expand=True)

    def on_login_success(self, utilisateur) -> None:
        self.utilisateur_courant = utilisateur
        self._vider()
        if utilisateur.role is RoleUtilisateur.ADMINISTRATEUR:
            self._frame_courante = AdminFrame(self, self)
        else:
            self._frame_courante = TeacherFrame(self, self)
        self._frame_courante.pack(fill="both", expand=True)

    def deconnexion(self) -> None:
        self.utilisateur_courant = None
        self._afficher_connexion()

    def rafraichir_listes_dependantes(self) -> None:
        """Permet à un onglet de signaler une modification (ex. nouvelle classe)
        afin que les autres onglets mettent à jour leurs combobox. Appelé
        après ajout d'élève/classe/matière/enseignant depuis AdminFrame."""
        if isinstance(self._frame_courante, AdminFrame):
            self._frame_courante.rafraichir_tout()
