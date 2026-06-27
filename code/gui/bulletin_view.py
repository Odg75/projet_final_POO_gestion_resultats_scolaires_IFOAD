"""Fenêtre d'aperçu d'un bulletin (trimestriel ou annuel pour le T3)."""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from models import Bulletin


class FenetreBulletin(tk.Toplevel):
    """Affiche un Bulletin dans une fenêtre dédiée, imprimable visuellement."""

    def __init__(self, parent, bulletin: Bulletin):
        super().__init__(parent)
        self.bulletin = bulletin
        self.title(f"Bulletin - {bulletin.eleve.nom_complet()} - Trimestre {bulletin.trimestre_numero}")
        # Hauteur de base pour un bulletin trimestriel ; plus haut si le
        # bulletin inclut en plus le bloc "Résultats annuels" (T3).
        hauteur = 560 if bulletin.est_bulletin_annuel else 460
        self.geometry(f"440x{hauteur}")
        self.resizable(False, False)
        self._construire()
        # Ajuste finement au contenu réel une fois les widgets construits,
        # au cas où la police ou la langue du système ferait varier les
        # hauteurs de ligne.
        self.update_idletasks()
        hauteur_reelle = self.winfo_reqheight() + 10
        if hauteur_reelle > hauteur:
            self.geometry(f"440x{hauteur_reelle}")

    def _construire(self) -> None:
        cadre = ttk.Frame(self, padding=18)
        cadre.pack(fill="both", expand=True)

        entete = ttk.Frame(cadre)
        entete.pack(fill="x", pady=(0, 12))
        ttk.Label(entete, text=self.bulletin.eleve.nom_complet(),
                  font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(entete, text=f"Année scolaire {self.bulletin.annee_libelle}",
                  foreground="#666666").pack(anchor="w")
        titre = (f"Bulletin du {self.bulletin.trimestre_numero}e trimestre"
                 + (" (avec résultats annuels)" if self.bulletin.est_bulletin_annuel else ""))
        ttk.Label(entete, text=titre, foreground="#0c447c").pack(anchor="w", pady=(4, 0))

        colonnes = ("matiere", "coefficient", "moyenne")
        arbre = ttk.Treeview(cadre, columns=colonnes, show="headings", height=8)
        arbre.heading("matiere", text="Matière")
        arbre.heading("coefficient", text="Coef.")
        arbre.heading("moyenne", text="Moyenne /20")
        arbre.column("matiere", width=180)
        arbre.column("coefficient", width=60, anchor="center")
        arbre.column("moyenne", width=90, anchor="center")
        for ligne in self.bulletin.lignes:
            arbre.insert("", "end", values=(ligne.matiere_nom, f"{ligne.coefficient:g}", f"{ligne.moyenne:.2f}"))
        arbre.pack(fill="x", pady=(0, 12))

        resultats = ttk.LabelFrame(cadre, text="Résultats du trimestre", padding=10)
        resultats.pack(fill="x", pady=(0, 12))
        self._ligne_resultat(resultats, "Moyenne du trimestre",
                              f"{self.bulletin.moyenne_trimestre:.2f} / 20" if self.bulletin.moyenne_trimestre is not None else "—")
        self._ligne_resultat(resultats, "Rang", f"{self.bulletin.rang_trimestre}e" if self.bulletin.rang_trimestre else "—")
        self._ligne_resultat(resultats, "Mention", self.bulletin.mention_trimestre or "—")

        if self.bulletin.est_bulletin_annuel:
            annuel = ttk.LabelFrame(cadre, text="Résultats annuels", padding=10)
            annuel.pack(fill="x")
            self._ligne_resultat(annuel, "Moyenne annuelle",
                                  f"{self.bulletin.moyenne_annuelle:.2f} / 20" if self.bulletin.moyenne_annuelle is not None else "—")
            self._ligne_resultat(annuel, "Rang annuel", f"{self.bulletin.rang_annuel}e" if self.bulletin.rang_annuel else "—")
            self._ligne_resultat(annuel, "Mention annuelle", self.bulletin.mention_annuelle or "—")
            self._ligne_resultat(annuel, "Décision", self.bulletin.decision_passage or "—", accent=True)

    @staticmethod
    def _ligne_resultat(parent, libelle: str, valeur: str, accent: bool = False) -> None:
        ligne = ttk.Frame(parent)
        ligne.pack(fill="x", pady=2)
        ttk.Label(ligne, text=libelle).pack(side="left")
        couleur = "#27500a" if accent else "#000000"
        ttk.Label(ligne, text=valeur, font=("Segoe UI", 9, "bold"), foreground=couleur).pack(side="right")
