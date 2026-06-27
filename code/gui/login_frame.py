"""Écran de connexion."""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from services import ErreurAuthentification


class LoginFrame(ttk.Frame):
    """Formulaire de connexion : identifiant / mot de passe."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=30)
        self.app = app
        self._construire()

    def _construire(self) -> None:
        conteneur = ttk.Frame(self, padding=24, relief="groove")
        conteneur.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(conteneur, text="Gestion des résultats scolaires",
                  font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(conteneur, text=f"Année scolaire {self.app.gestionnaire.annee_scolaire.libelle}",
                  foreground="#666666").grid(row=1, column=0, columnspan=2, pady=(0, 18))

        ttk.Label(conteneur, text="Identifiant").grid(row=2, column=0, sticky="w", pady=4)
        self.var_identifiant = tk.StringVar()
        ttk.Entry(conteneur, textvariable=self.var_identifiant, width=28).grid(row=2, column=1, pady=4)

        ttk.Label(conteneur, text="Mot de passe").grid(row=3, column=0, sticky="w", pady=4)
        self.var_mot_de_passe = tk.StringVar()
        entree_mdp = ttk.Entry(conteneur, textvariable=self.var_mot_de_passe, show="•", width=28)
        entree_mdp.grid(row=3, column=1, pady=4)
        entree_mdp.bind("<Return>", lambda _evt: self._connexion())

        bouton = ttk.Button(conteneur, text="Se connecter", command=self._connexion)
        bouton.grid(row=4, column=0, columnspan=2, pady=(16, 4), sticky="ew")

        ttk.Label(conteneur, text="Compte Administrateur (Directeur, Secrétariat) ou Enseignant",
                  foreground="#888888", font=("Segoe UI", 8)).grid(row=5, column=0, columnspan=2, pady=(8, 0))

    def _connexion(self) -> None:
        identifiant = self.var_identifiant.get().strip()
        mot_de_passe = self.var_mot_de_passe.get()
        if not identifiant or not mot_de_passe:
            messagebox.showwarning("Connexion", "Veuillez renseigner l'identifiant et le mot de passe.")
            return
        try:
            utilisateur = self.app.auth_service.authentifier(identifiant, mot_de_passe)
        except ErreurAuthentification as exc:
            messagebox.showerror("Connexion refusée", str(exc))
            return
        self.var_mot_de_passe.set("")
        self.app.on_login_success(utilisateur)
