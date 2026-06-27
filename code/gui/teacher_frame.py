"""Tableau de bord Enseignant : accès restreint à ses classes et sa/ses matière(s)."""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from .chart_widgets import GraphiqueBarres


class TeacherFrame(ttk.Frame):
    """Interface restreinte : classes affectées, saisie des notes, statistiques."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.gr = app.gestionnaire
        self.utilisateur = app.utilisateur_courant
        self.enseignant = self.utilisateur.enseignant
        self._lignes_saisie: list[tuple] = []  # (eleve, var_note, var_statut)
        self._construire()

    # ------------------------------------------------------------------ #
    def _construire(self) -> None:
        entete = ttk.Frame(self)
        entete.pack(fill="x", pady=(0, 8))
        ttk.Label(entete, text=f"Espace Enseignant — {self.enseignant.nom_complet()}",
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(entete, text="Déconnexion", command=self.app.deconnexion).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._onglet_mes_classes()
        self._onglet_saisie_notes()
        self._onglet_mes_statistiques()

    # ===================== Onglet MES CLASSES ===================== #
    def _onglet_mes_classes(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Mes classes")

        arbre = ttk.Treeview(onglet, columns=("classe", "niveau", "matiere", "effectif"),
                              show="headings", height=12)
        for cle, texte, largeur in (("classe", "Classe", 120), ("niveau", "Niveau", 100),
                                     ("matiere", "Matière", 140), ("effectif", "Effectif", 80)):
            arbre.heading(cle, text=texte)
            arbre.column(cle, width=largeur)
        arbre.pack(fill="both", expand=True)

        for affectation in self.enseignant.affectations:
            arbre.insert("", "end", values=(affectation.classe.nom, affectation.classe.niveau,
                                             affectation.matiere.nom, affectation.classe.effectif))

    # ===================== Onglet SAISIE DES NOTES ===================== #
    def _onglet_saisie_notes(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Saisie des notes")

        selection = ttk.Frame(onglet)
        selection.pack(fill="x", pady=(0, 10))
        self.var_classe = tk.StringVar()
        self.var_matiere = tk.StringVar()
        self.var_trimestre = tk.StringVar(value="1")

        classes = sorted({a.classe for a in self.enseignant.affectations}, key=lambda c: c.nom)
        self.combo_classe = ttk.Combobox(selection, textvariable=self.var_classe, width=14,
                                          state="readonly", values=[c.nom for c in classes])
        self.combo_classe.bind("<<ComboboxSelected>>", lambda _e: self._maj_combo_matieres())
        self.combo_matiere = ttk.Combobox(selection, textvariable=self.var_matiere, width=14, state="readonly")

        ttk.Label(selection, text="Classe").grid(row=0, column=0, sticky="w")
        self.combo_classe.grid(row=0, column=1, padx=4)
        ttk.Label(selection, text="Matière").grid(row=0, column=2, sticky="w")
        self.combo_matiere.grid(row=0, column=3, padx=4)
        ttk.Label(selection, text="Trimestre").grid(row=0, column=4, sticky="w")
        ttk.Combobox(selection, textvariable=self.var_trimestre, values=("1", "2", "3"),
                     width=4, state="readonly").grid(row=0, column=5, padx=4)
        ttk.Button(selection, text="Charger les élèves", command=self._charger_eleves).grid(row=0, column=6, padx=6)

        entete_table = ttk.Frame(onglet)
        entete_table.pack(fill="x")
        ttk.Label(entete_table, text="Élève", width=28).pack(side="left")
        ttk.Label(entete_table, text="Note /20", width=10).pack(side="left")
        ttk.Label(entete_table, text="Statut", width=12).pack(side="left")

        self.cadre_table = ttk.Frame(onglet)
        self.cadre_table.pack(fill="both", expand=True, pady=(4, 8))

        ttk.Button(onglet, text="Enregistrer les notes", command=self._enregistrer_notes).pack(anchor="e")

    def _maj_combo_matieres(self) -> None:
        classe = self.gr.trouver_classe(self.var_classe.get())
        if not classe:
            self.combo_matiere["values"] = []
            return
        matieres = [a.matiere for a in self.enseignant.affectations if a.classe == classe]
        self.combo_matiere["values"] = [m.nom for m in matieres]

    def _charger_eleves(self) -> None:
        classe = self.gr.trouver_classe(self.var_classe.get())
        matiere = self.gr.trouver_matiere(self.var_matiere.get())
        if not (classe and matiere) or not self.enseignant.enseigne_a(classe, matiere):
            messagebox.showwarning("Saisie des notes", "Veuillez sélectionner une classe et une matière qui vous sont affectées.")
            return

        for widget in self.cadre_table.winfo_children():
            widget.destroy()
        self._lignes_saisie.clear()

        trimestre = self.gr.annee_scolaire.trimestre(int(self.var_trimestre.get()))
        for eleve in classe.eleves:
            note_existante = next((n for n in trimestre.notes_de(eleve) if n.matiere == matiere), None)
            var_note = tk.StringVar(value=str(note_existante.valeur) if note_existante else "")
            statut = note_existante.statut.value if note_existante else "À saisir"

            ligne = ttk.Frame(self.cadre_table)
            ligne.pack(fill="x", pady=1)
            ttk.Label(ligne, text=eleve.nom_complet(), width=28).pack(side="left")
            entree = ttk.Entry(ligne, textvariable=var_note, width=10)
            verrouillee = note_existante is not None and not note_existante.est_modifiable()
            if verrouillee:
                entree.configure(state="disabled")
            entree.pack(side="left")
            ttk.Label(ligne, text=statut, width=12,
                      foreground="#27500a" if statut == "Validée" else "#633806").pack(side="left")

            self._lignes_saisie.append((eleve, var_note, verrouillee))

    def _enregistrer_notes(self) -> None:
        matiere = self.gr.trouver_matiere(self.var_matiere.get())
        trimestre_numero = int(self.var_trimestre.get())
        if not matiere or not self._lignes_saisie:
            messagebox.showwarning("Saisie des notes", "Veuillez d'abord charger une liste d'élèves.")
            return

        erreurs = []
        enregistrees = 0
        for eleve, var_note, verrouillee in self._lignes_saisie:
            if verrouillee:
                continue
            texte = var_note.get().strip()
            if not texte:
                continue
            try:
                self.gr.saisir_note(eleve, matiere, trimestre_numero, float(texte))
                enregistrees += 1
            except (ValueError, PermissionError) as exc:
                erreurs.append(f"{eleve.nom_complet()} : {exc}")

        message = f"{enregistrees} note(s) enregistrée(s) en brouillon."
        if erreurs:
            message += "\n\nErreurs :\n" + "\n".join(erreurs)
        messagebox.showinfo("Saisie des notes", message)
        self._charger_eleves()

    # ===================== Onglet MES STATISTIQUES ===================== #
    def _onglet_mes_statistiques(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Mes statistiques")

        selection = ttk.Frame(onglet)
        selection.pack(fill="x", pady=(0, 10))
        self.var_stats_classe = tk.StringVar()
        self.var_stats_matiere = tk.StringVar()
        self.var_stats_trimestre = tk.StringVar(value="1")

        classes = sorted({a.classe for a in self.enseignant.affectations}, key=lambda c: c.nom)
        self.combo_stats_classe = ttk.Combobox(selection, textvariable=self.var_stats_classe, width=14,
                                                state="readonly", values=[c.nom for c in classes])
        self.combo_stats_classe.bind("<<ComboboxSelected>>", lambda _e: self._maj_combo_stats_matieres())
        self.combo_stats_matiere = ttk.Combobox(selection, textvariable=self.var_stats_matiere,
                                                 width=14, state="readonly")

        ttk.Label(selection, text="Classe").grid(row=0, column=0, sticky="w")
        self.combo_stats_classe.grid(row=0, column=1, padx=4)
        ttk.Label(selection, text="Matière").grid(row=0, column=2, sticky="w")
        self.combo_stats_matiere.grid(row=0, column=3, padx=4)
        ttk.Label(selection, text="Trimestre").grid(row=0, column=4, sticky="w")
        ttk.Combobox(selection, textvariable=self.var_stats_trimestre, values=("1", "2", "3"),
                     width=4, state="readonly").grid(row=0, column=5, padx=4)
        ttk.Button(selection, text="Analyser", command=self._analyser).grid(row=0, column=6, padx=6)

        self.cadre_resume = ttk.Frame(onglet)
        self.cadre_resume.pack(fill="x", pady=(0, 10))
        self.cadre_graphique = ttk.Frame(onglet)
        self.cadre_graphique.pack(fill="both", expand=True)

    def _maj_combo_stats_matieres(self) -> None:
        classe = self.gr.trouver_classe(self.var_stats_classe.get())
        if not classe:
            self.combo_stats_matiere["values"] = []
            return
        matieres = [a.matiere for a in self.enseignant.affectations if a.classe == classe]
        self.combo_stats_matiere["values"] = [m.nom for m in matieres]

    def _analyser(self) -> None:
        classe = self.gr.trouver_classe(self.var_stats_classe.get())
        matiere = self.gr.trouver_matiere(self.var_stats_matiere.get())
        if not (classe and matiere) or not self.enseignant.enseigne_a(classe, matiere):
            messagebox.showwarning("Statistiques", "Veuillez sélectionner une classe et une matière qui vous sont affectées.")
            return
        trimestre_numero = int(self.var_stats_trimestre.get())
        analyseur = self.app.analyseur_statistique

        for widget in self.cadre_resume.winfo_children():
            widget.destroy()
        for widget in self.cadre_graphique.winfo_children():
            widget.destroy()

        moyenne_matiere = analyseur.moyenne_matiere(classe, matiere, trimestre_numero)
        carte = ttk.LabelFrame(self.cadre_resume, text=f"Moyenne de la classe en {matiere.nom}", padding=8)
        carte.pack(side="left")
        ttk.Label(carte, text=f"{moyenne_matiere:.2f} / 20" if moyenne_matiere is not None else "—",
                  font=("Segoe UI", 11, "bold")).pack()

        trimestre = self.gr.annee_scolaire.trimestre(trimestre_numero)
        notes_par_eleve = {f"{e.prenom[0]}.{e.nom}": n.valeur
                            for e in classe.eleves
                            for n in trimestre.notes_de(e) if n.matiere == matiere}
        GraphiqueBarres(self.cadre_graphique, notes_par_eleve,
                         titre=f"Notes en {matiere.nom}").pack(side="left", padx=8, pady=8)
