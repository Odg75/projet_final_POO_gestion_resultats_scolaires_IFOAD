"""Petits graphiques (barres, camembert) dessinés sur un Canvas Tkinter.

Volontairement sans dépendance externe (pas de matplotlib) afin que le
projet fonctionne avec la seule bibliothèque standard de Python.
"""

from __future__ import annotations
import tkinter as tk
from typing import Dict

PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#eb6834", "#e34948", "#4a3aa7"]


class GraphiqueBarres(tk.Canvas):
    """Histogramme simple : un dict {étiquette: valeur}."""

    def __init__(self, parent, donnees: Dict[str, float], titre: str = "",
                 largeur: int = 360, hauteur: int = 220, **kwargs):
        super().__init__(parent, width=largeur, height=hauteur, bg="white",
                          highlightthickness=1, highlightbackground="#dddddd", **kwargs)
        self.donnees = donnees
        self.titre = titre
        self.largeur = largeur
        self.hauteur = hauteur
        self.dessiner()

    def dessiner(self) -> None:
        self.delete("all")
        marge_bas, marge_haut, marge_cote = 36, 26, 16
        zone_haut = marge_haut
        zone_bas = self.hauteur - marge_bas
        zone_largeur = self.largeur - 2 * marge_cote

        if self.titre:
            self.create_text(self.largeur / 2, 12, text=self.titre, font=("Segoe UI", 9, "bold"))

        if not self.donnees:
            self.create_text(self.largeur / 2, self.hauteur / 2, text="Aucune donnée")
            return

        valeur_max = max(self.donnees.values()) or 1
        nb_barres = len(self.donnees)
        largeur_barre = zone_largeur / nb_barres * 0.6
        espacement = zone_largeur / nb_barres

        self.create_line(marge_cote, zone_bas, self.largeur - marge_cote, zone_bas, fill="#999999")

        for index, (etiquette, valeur) in enumerate(self.donnees.items()):
            hauteur_barre = (valeur / valeur_max) * (zone_bas - zone_haut) if valeur_max else 0
            x_centre = marge_cote + espacement * index + espacement / 2
            x0 = x_centre - largeur_barre / 2
            x1 = x_centre + largeur_barre / 2
            y0 = zone_bas - hauteur_barre
            couleur = PALETTE[index % len(PALETTE)]
            self.create_rectangle(x0, y0, x1, zone_bas, fill=couleur, outline="")
            self.create_text(x_centre, y0 - 8, text=str(valeur), font=("Segoe UI", 8))
            self.create_text(x_centre, zone_bas + 12, text=etiquette, font=("Segoe UI", 8))


class GraphiqueCamembert(tk.Canvas):
    """Diagramme circulaire simple : un dict {étiquette: valeur}."""

    def __init__(self, parent, donnees: Dict[str, float], titre: str = "",
                 largeur: int = 280, hauteur: int = 220, **kwargs):
        super().__init__(parent, width=largeur, height=hauteur, bg="white",
                          highlightthickness=1, highlightbackground="#dddddd", **kwargs)
        self.donnees = donnees
        self.titre = titre
        self.largeur = largeur
        self.hauteur = hauteur
        self.dessiner()

    def dessiner(self) -> None:
        self.delete("all")
        if self.titre:
            self.create_text(self.largeur / 2, 12, text=self.titre, font=("Segoe UI", 9, "bold"))

        total = sum(self.donnees.values())
        diametre = min(self.largeur, self.hauteur) - 70
        x0 = 20
        y0 = 28
        x1 = x0 + diametre
        y1 = y0 + diametre

        if not self.donnees or total == 0:
            self.create_text(self.largeur / 2, self.hauteur / 2, text="Aucune donnée")
            return

        angle_depart = 0.0
        legende_y = 30
        for index, (etiquette, valeur) in enumerate(self.donnees.items()):
            angle_extent = 360 * valeur / total
            couleur = PALETTE[index % len(PALETTE)]
            if valeur > 0:
                self.create_arc(x0, y0, x1, y1, start=angle_depart, extent=angle_extent,
                                 fill=couleur, outline="white")
            angle_depart += angle_extent

            self.create_rectangle(x1 + 14, legende_y, x1 + 24, legende_y + 10, fill=couleur, outline="")
            self.create_text(x1 + 30, legende_y + 5, anchor="w",
                              text=f"{etiquette} ({valeur})", font=("Segoe UI", 8))
            legende_y += 18
