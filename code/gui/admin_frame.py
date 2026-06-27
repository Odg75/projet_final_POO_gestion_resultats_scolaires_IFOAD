"""Tableau de bord Administrateur (Directeur / Secrétariat) : accès complet."""

from __future__ import annotations
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from models import Eleve, Enseignant, Matiere, Classe
from .bulletin_view import FenetreBulletin
from .chart_widgets import GraphiqueBarres, GraphiqueCamembert


class AdminFrame(ttk.Frame):
    """Interface complète : élèves, classes, matières, enseignants, notes,
    bulletins et statistiques."""

    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app
        self.gr = app.gestionnaire
        self._construire()

    # ------------------------------------------------------------------ #
    def _construire(self) -> None:
        entete = ttk.Frame(self)
        entete.pack(fill="x", pady=(0, 8))
        ttk.Label(entete, text="Espace Administrateur", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(entete, text="Déconnexion", command=self.app.deconnexion).pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._onglet_eleves()
        self._onglet_classes()
        self._onglet_matieres()
        self._onglet_enseignants()
        self._onglet_notes()
        self._onglet_bulletins()
        self._onglet_statistiques()

    def rafraichir_tout(self) -> None:
        self._rafraichir_eleves()
        self._rafraichir_classes()
        self._rafraichir_matieres()
        self._rafraichir_enseignants()
        self._rafraichir_combos_notes()
        self._rafraichir_combos_bulletins()
        self._rafraichir_combos_stats()

    # ===================== Onglet ELEVES ===================== #
    def _onglet_eleves(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Élèves")

        formulaire = ttk.LabelFrame(onglet, text="Ajouter un élève", padding=10)
        formulaire.pack(fill="x", pady=(0, 10))

        self.var_eleve_nom = tk.StringVar()
        self.var_eleve_prenom = tk.StringVar()
        self.var_eleve_date = tk.StringVar(value="2010-01-01")
        self.var_eleve_sexe = tk.StringVar(value="F")
        self.var_eleve_classe = tk.StringVar()

        ttk.Label(formulaire, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_eleve_nom, width=16).grid(row=0, column=1, padx=4)
        ttk.Label(formulaire, text="Prénom").grid(row=0, column=2, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_eleve_prenom, width=16).grid(row=0, column=3, padx=4)
        ttk.Label(formulaire, text="Naissance (AAAA-MM-JJ)").grid(row=0, column=4, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_eleve_date, width=12).grid(row=0, column=5, padx=4)

        ttk.Label(formulaire, text="Sexe").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Combobox(formulaire, textvariable=self.var_eleve_sexe, values=("F", "M"),
                     width=4, state="readonly").grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Label(formulaire, text="Classe").grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.combo_eleve_classe = ttk.Combobox(formulaire, textvariable=self.var_eleve_classe,
                                                width=14, state="readonly")
        self.combo_eleve_classe.grid(row=1, column=3, sticky="w", pady=(6, 0))
        ttk.Button(formulaire, text="Ajouter", command=self._ajouter_eleve).grid(row=1, column=5, pady=(6, 0))

        filtre = ttk.Frame(onglet)
        filtre.pack(fill="x", pady=(0, 6))

        ttk.Label(filtre, text="Rechercher").pack(side="left")
        self.var_eleve_recherche = tk.StringVar()
        entree_recherche = ttk.Entry(filtre, textvariable=self.var_eleve_recherche, width=22)
        entree_recherche.pack(side="left", padx=(4, 12))
        self.var_eleve_recherche.trace_add("write", lambda *_args: self._filtrer_eleves())

        ttk.Label(filtre, text="Classe").pack(side="left")
        self.var_eleve_filtre_classe = tk.StringVar(value="Toutes les classes")
        self.combo_eleve_filtre_classe = ttk.Combobox(filtre, textvariable=self.var_eleve_filtre_classe,
                                                        width=16, state="readonly")
        self.combo_eleve_filtre_classe.pack(side="left", padx=(4, 12))
        self.combo_eleve_filtre_classe.bind("<<ComboboxSelected>>", lambda _e: self._filtrer_eleves())

        ttk.Button(filtre, text="Réinitialiser", command=self._reinitialiser_filtres_eleves).pack(side="left")

        self.label_nb_eleves = ttk.Label(filtre, text="")
        self.label_nb_eleves.pack(side="right")

        self.arbre_eleves = ttk.Treeview(onglet, columns=("matricule", "nom", "classe", "age"),
                                          show="headings", height=12)
        for cle, texte, largeur in (("matricule", "Matricule", 90), ("nom", "Nom complet", 200),
                                     ("classe", "Classe", 100), ("age", "Âge", 60)):
            self.arbre_eleves.heading(cle, text=texte)
            self.arbre_eleves.column(cle, width=largeur, anchor="w")
        self.arbre_eleves.pack(fill="both", expand=True)

        actions_eleves = ttk.Frame(onglet)
        actions_eleves.pack(fill="x", pady=(6, 0))
        ttk.Button(actions_eleves, text="Modifier l'élève sélectionné",
                   command=self._modifier_eleve).pack(side="right", padx=(6, 0))
        ttk.Button(actions_eleves, text="Supprimer l'élève sélectionné",
                   command=self._supprimer_eleve).pack(side="right")

        self._rafraichir_eleves()

    def _ajouter_eleve(self) -> None:
        try:
            date_naissance = datetime.date.fromisoformat(self.var_eleve_date.get().strip())
            classe = self.gr.trouver_classe(self.var_eleve_classe.get())
            if classe is None:
                raise ValueError("Veuillez sélectionner une classe valide.")
            eleve = Eleve(self.var_eleve_nom.get(), self.var_eleve_prenom.get(),
                          date_naissance, self.var_eleve_sexe.get())
            self.gr.ajouter_eleve(eleve, classe)
        except Exception as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return
        self.var_eleve_nom.set("")
        self.var_eleve_prenom.set("")
        self._rafraichir_eleves()
        self._rafraichir_classes()
        self.app.rafraichir_listes_dependantes()

    def _supprimer_eleve(self) -> None:
        selection = self.arbre_eleves.selection()
        if not selection:
            return
        matricule = self.arbre_eleves.item(selection[0], "values")[0]
        eleve = next((e for e in self.gr.eleves if e.matricule == matricule), None)
        if eleve and messagebox.askyesno("Confirmation", f"Supprimer {eleve.nom_complet()} ?"):
            self.gr.supprimer_eleve(eleve)
            self._rafraichir_eleves()
            self._rafraichir_classes()

    def _modifier_eleve(self) -> None:
        selection = self.arbre_eleves.selection()
        if not selection:
            messagebox.showinfo("Modifier", "Veuillez sélectionner un élève dans la liste.")
            return
        matricule = self.arbre_eleves.item(selection[0], "values")[0]
        eleve = next((e for e in self.gr.eleves if e.matricule == matricule), None)
        if not eleve:
            return

        fenetre = tk.Toplevel(self)
        fenetre.title(f"Modifier {eleve.nom_complet()}")
        fenetre.resizable(False, False)
        fenetre.transient(self.winfo_toplevel())
        fenetre.grab_set()

        cadre = ttk.Frame(fenetre, padding=14)
        cadre.pack(fill="both", expand=True)

        var_nom = tk.StringVar(value=eleve.nom)
        var_prenom = tk.StringVar(value=eleve.prenom)
        var_date = tk.StringVar(value=eleve.date_naissance.isoformat())
        var_sexe = tk.StringVar(value=eleve.sexe)
        var_classe = tk.StringVar(value=eleve.classe.nom if eleve.classe else "")

        ttk.Label(cadre, text="Nom").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=var_nom, width=22).grid(row=0, column=1, pady=4)
        ttk.Label(cadre, text="Prénom").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=var_prenom, width=22).grid(row=1, column=1, pady=4)
        ttk.Label(cadre, text="Naissance (AAAA-MM-JJ)").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=var_date, width=22).grid(row=2, column=1, pady=4)
        ttk.Label(cadre, text="Sexe").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(cadre, textvariable=var_sexe, values=("F", "M"),
                     width=19, state="readonly").grid(row=3, column=1, pady=4)
        ttk.Label(cadre, text="Classe").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(cadre, textvariable=var_classe, values=[c.nom for c in self.gr.classes],
                     width=19, state="readonly").grid(row=4, column=1, pady=4)

        def _enregistrer() -> None:
            try:
                date_naissance = datetime.date.fromisoformat(var_date.get().strip())
                nouvelle_classe = self.gr.trouver_classe(var_classe.get())
                if nouvelle_classe is None:
                    raise ValueError("Veuillez sélectionner une classe valide.")
                self.gr.modifier_eleve(eleve, nom=var_nom.get(), prenom=var_prenom.get(),
                                        date_naissance=date_naissance, sexe=var_sexe.get(),
                                        nouvelle_classe=nouvelle_classe)
            except Exception as exc:
                messagebox.showerror("Modification impossible", str(exc))
                return
            fenetre.destroy()
            self._rafraichir_eleves()
            self._rafraichir_classes()

        boutons = ttk.Frame(cadre)
        boutons.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(boutons, text="Annuler", command=fenetre.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(boutons, text="Enregistrer", command=_enregistrer).pack(side="right")

    def _rafraichir_eleves(self) -> None:
        self.combo_eleve_classe["values"] = [c.nom for c in self.gr.classes]
        if hasattr(self, "combo_eleve_filtre_classe"):
            self.combo_eleve_filtre_classe["values"] = ["Toutes les classes"] + [c.nom for c in self.gr.classes]
        self._filtrer_eleves()

    def _filtrer_eleves(self) -> None:
        recherche = self.var_eleve_recherche.get().strip().lower()
        classe_filtre = self.var_eleve_filtre_classe.get()

        eleves_filtres = []
        for eleve in self.gr.eleves:
            if classe_filtre and classe_filtre != "Toutes les classes":
                if not eleve.classe or eleve.classe.nom != classe_filtre:
                    continue
            if recherche:
                cible = f"{eleve.matricule} {eleve.nom_complet()}".lower()
                if recherche not in cible:
                    continue
            eleves_filtres.append(eleve)

        for ligne in self.arbre_eleves.get_children():
            self.arbre_eleves.delete(ligne)
        for eleve in eleves_filtres:
            classe_nom = eleve.classe.nom if eleve.classe else "—"
            self.arbre_eleves.insert("", "end", values=(eleve.matricule, eleve.nom_complet(),
                                                          classe_nom, eleve.age()))

        total = len(self.gr.eleves)
        affiches = len(eleves_filtres)
        if affiches == total:
            self.label_nb_eleves.config(text=f"{total} élève(s)")
        else:
            self.label_nb_eleves.config(text=f"{affiches} / {total} élève(s)")

    def _reinitialiser_filtres_eleves(self) -> None:
        self.var_eleve_recherche.set("")
        self.var_eleve_filtre_classe.set("Toutes les classes")
        self._filtrer_eleves()

    # ===================== Onglet CLASSES ===================== #
    def _onglet_classes(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Classes")

        formulaire = ttk.LabelFrame(onglet, text="Ajouter une classe", padding=10)
        formulaire.pack(fill="x", pady=(0, 10))
        self.var_classe_nom = tk.StringVar()
        self.var_classe_niveau = tk.StringVar()
        ttk.Label(formulaire, text="Nom (ex. 3ème A)").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_classe_nom, width=16).grid(row=0, column=1, padx=4)
        ttk.Label(formulaire, text="Niveau (ex. 3ème)").grid(row=0, column=2, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_classe_niveau, width=16).grid(row=0, column=3, padx=4)
        ttk.Button(formulaire, text="Ajouter", command=self._ajouter_classe).grid(row=0, column=4, padx=6)

        self.arbre_classes = ttk.Treeview(onglet, columns=("nom", "niveau", "effectif"),
                                           show="headings", height=12)
        for cle, texte, largeur in (("nom", "Classe", 140), ("niveau", "Niveau", 120), ("effectif", "Effectif", 80)):
            self.arbre_classes.heading(cle, text=texte)
            self.arbre_classes.column(cle, width=largeur)
        self.arbre_classes.pack(fill="both", expand=True)

        self._rafraichir_classes()

    def _ajouter_classe(self) -> None:
        try:
            classe = Classe(self.var_classe_nom.get(), self.var_classe_niveau.get())
            self.gr.ajouter_classe(classe)
        except Exception as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return
        self.var_classe_nom.set("")
        self.var_classe_niveau.set("")
        self._rafraichir_classes()
        self.app.rafraichir_listes_dependantes()

    def _rafraichir_classes(self) -> None:
        for ligne in self.arbre_classes.get_children():
            self.arbre_classes.delete(ligne)
        for classe in self.gr.classes:
            self.arbre_classes.insert("", "end", values=(classe.nom, classe.niveau, classe.effectif))
        if hasattr(self, "combo_eleve_classe"):
            self.combo_eleve_classe["values"] = [c.nom for c in self.gr.classes]
        if hasattr(self, "combo_eleve_filtre_classe"):
            self.combo_eleve_filtre_classe["values"] = ["Toutes les classes"] + [c.nom for c in self.gr.classes]

    # ===================== Onglet MATIERES ===================== #
    def _onglet_matieres(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Matières")

        formulaire = ttk.LabelFrame(onglet, text="Ajouter une matière", padding=10)
        formulaire.pack(fill="x", pady=(0, 10))
        self.var_matiere_nom = tk.StringVar()
        self.var_matiere_coef = tk.StringVar(value="1")
        ttk.Label(formulaire, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_matiere_nom, width=18).grid(row=0, column=1, padx=4)
        ttk.Label(formulaire, text="Coefficient").grid(row=0, column=2, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_matiere_coef, width=6).grid(row=0, column=3, padx=4)
        ttk.Button(formulaire, text="Ajouter", command=self._ajouter_matiere).grid(row=0, column=4, padx=6)

        self.arbre_matieres = ttk.Treeview(onglet, columns=("nom", "coefficient"), show="headings", height=12)
        self.arbre_matieres.heading("nom", text="Matière")
        self.arbre_matieres.heading("coefficient", text="Coefficient")
        self.arbre_matieres.column("nom", width=200)
        self.arbre_matieres.column("coefficient", width=100)
        self.arbre_matieres.pack(fill="both", expand=True)

        self._rafraichir_matieres()

    def _ajouter_matiere(self) -> None:
        try:
            matiere = Matiere(self.var_matiere_nom.get(), self.var_matiere_coef.get())
            self.gr.ajouter_matiere(matiere)
        except Exception as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return
        self.var_matiere_nom.set("")
        self.var_matiere_coef.set("1")
        self._rafraichir_matieres()
        self.app.rafraichir_listes_dependantes()

    def _rafraichir_matieres(self) -> None:
        for ligne in self.arbre_matieres.get_children():
            self.arbre_matieres.delete(ligne)
        for matiere in self.gr.matieres:
            self.arbre_matieres.insert("", "end", values=(matiere.nom, f"{matiere.coefficient:g}"))

    # ===================== Onglet ENSEIGNANTS / AFFECTATIONS ===================== #
    def _onglet_enseignants(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Enseignants")

        formulaire = ttk.LabelFrame(onglet, text="Ajouter un enseignant (+ compte)", padding=10)
        formulaire.pack(fill="x", pady=(0, 10))
        self.var_ens_nom = tk.StringVar()
        self.var_ens_prenom = tk.StringVar()
        self.var_ens_specialite = tk.StringVar()
        self.var_ens_identifiant = tk.StringVar()
        self.var_ens_mdp = tk.StringVar(value="changer123")

        ttk.Label(formulaire, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_ens_nom, width=14).grid(row=0, column=1, padx=4)
        ttk.Label(formulaire, text="Prénom").grid(row=0, column=2, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_ens_prenom, width=14).grid(row=0, column=3, padx=4)
        ttk.Label(formulaire, text="Spécialité").grid(row=0, column=4, sticky="w")
        ttk.Entry(formulaire, textvariable=self.var_ens_specialite, width=14).grid(row=0, column=5, padx=4)

        ttk.Label(formulaire, text="Identifiant").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(formulaire, textvariable=self.var_ens_identifiant, width=14).grid(row=1, column=1, pady=(6, 0))
        ttk.Label(formulaire, text="Mot de passe").grid(row=1, column=2, sticky="w", pady=(6, 0))
        ttk.Entry(formulaire, textvariable=self.var_ens_mdp, width=14, show="•").grid(row=1, column=3, pady=(6, 0))
        ttk.Button(formulaire, text="Ajouter", command=self._ajouter_enseignant).grid(row=1, column=5, pady=(6, 0))

        self.arbre_enseignants = ttk.Treeview(onglet, columns=("code", "nom", "specialite", "affectations"),
                                               show="headings", height=8)
        for cle, texte, largeur in (("code", "Code", 70), ("nom", "Nom", 160),
                                     ("specialite", "Spécialité", 120), ("affectations", "Affectations", 220)):
            self.arbre_enseignants.heading(cle, text=texte)
            self.arbre_enseignants.column(cle, width=largeur)
        self.arbre_enseignants.pack(fill="both", expand=True, pady=(0, 10))

        affectation = ttk.LabelFrame(onglet, text="Affecter un enseignant à une classe / matière", padding=10)
        affectation.pack(fill="x")
        self.var_aff_enseignant = tk.StringVar()
        self.var_aff_classe = tk.StringVar()
        self.var_aff_matiere = tk.StringVar()
        self.combo_aff_enseignant = ttk.Combobox(affectation, textvariable=self.var_aff_enseignant,
                                                  width=18, state="readonly")
        self.combo_aff_classe = ttk.Combobox(affectation, textvariable=self.var_aff_classe,
                                              width=14, state="readonly")
        self.combo_aff_matiere = ttk.Combobox(affectation, textvariable=self.var_aff_matiere,
                                               width=14, state="readonly")
        ttk.Label(affectation, text="Enseignant").grid(row=0, column=0, sticky="w")
        self.combo_aff_enseignant.grid(row=0, column=1, padx=4)
        ttk.Label(affectation, text="Classe").grid(row=0, column=2, sticky="w")
        self.combo_aff_classe.grid(row=0, column=3, padx=4)
        ttk.Label(affectation, text="Matière").grid(row=0, column=4, sticky="w")
        self.combo_aff_matiere.grid(row=0, column=5, padx=4)
        ttk.Button(affectation, text="Affecter", command=self._affecter).grid(row=0, column=6, padx=6)

        self._rafraichir_enseignants()

    def _ajouter_enseignant(self) -> None:
        try:
            enseignant = Enseignant(self.var_ens_nom.get(), self.var_ens_prenom.get(),
                                     datetime.date(1985, 1, 1), "M", specialite=self.var_ens_specialite.get())
            self.gr.ajouter_enseignant(enseignant)
            identifiant = self.var_ens_identifiant.get().strip() or enseignant.code.lower()
            self.gr.creer_compte_enseignant(identifiant, self.var_ens_mdp.get(), enseignant)
        except Exception as exc:
            messagebox.showerror("Ajout impossible", str(exc))
            return
        self.var_ens_nom.set("")
        self.var_ens_prenom.set("")
        self.var_ens_specialite.set("")
        self.var_ens_identifiant.set("")
        self._rafraichir_enseignants()
        self.app.rafraichir_listes_dependantes()

    def _affecter(self) -> None:
        enseignant = next((e for e in self.gr.enseignants
                            if f"{e.code} - {e.nom_complet()}" == self.var_aff_enseignant.get()), None)
        classe = self.gr.trouver_classe(self.var_aff_classe.get())
        matiere = self.gr.trouver_matiere(self.var_aff_matiere.get())
        if not (enseignant and classe and matiere):
            messagebox.showwarning("Affectation", "Veuillez sélectionner un enseignant, une classe et une matière.")
            return
        try:
            self.gr.affecter(enseignant, classe, matiere)
        except Exception as exc:
            messagebox.showerror("Affectation impossible", str(exc))
            return
        self._rafraichir_enseignants()

    def _rafraichir_enseignants(self) -> None:
        for ligne in self.arbre_enseignants.get_children():
            self.arbre_enseignants.delete(ligne)
        for enseignant in self.gr.enseignants:
            affectations = ", ".join(f"{a.classe.nom}/{a.matiere.nom}" for a in enseignant.affectations)
            self.arbre_enseignants.insert("", "end", values=(enseignant.code, enseignant.nom_complet(),
                                                              enseignant.specialite, affectations or "—"))
        if hasattr(self, "combo_aff_enseignant"):
            self.combo_aff_enseignant["values"] = [f"{e.code} - {e.nom_complet()}" for e in self.gr.enseignants]
            self.combo_aff_classe["values"] = [c.nom for c in self.gr.classes]
            self.combo_aff_matiere["values"] = [m.nom for m in self.gr.matieres]

    # ===================== Onglet NOTES (validation) ===================== #
    def _onglet_notes(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Notes à valider")

        selection = ttk.Frame(onglet)
        selection.pack(fill="x", pady=(0, 10))
        self.var_notes_classe = tk.StringVar()
        self.var_notes_matiere = tk.StringVar()
        self.var_notes_trimestre = tk.StringVar(value="1")
        self.combo_notes_classe = ttk.Combobox(selection, textvariable=self.var_notes_classe,
                                                width=14, state="readonly")
        self.combo_notes_matiere = ttk.Combobox(selection, textvariable=self.var_notes_matiere,
                                                 width=14, state="readonly")
        ttk.Label(selection, text="Classe").grid(row=0, column=0, sticky="w")
        self.combo_notes_classe.grid(row=0, column=1, padx=4)
        ttk.Label(selection, text="Matière").grid(row=0, column=2, sticky="w")
        self.combo_notes_matiere.grid(row=0, column=3, padx=4)
        ttk.Label(selection, text="Trimestre").grid(row=0, column=4, sticky="w")
        ttk.Combobox(selection, textvariable=self.var_notes_trimestre, values=("1", "2", "3"),
                     width=4, state="readonly").grid(row=0, column=5, padx=4)
        ttk.Button(selection, text="Afficher", command=self._afficher_notes).grid(row=0, column=6, padx=6)
        ttk.Button(selection, text="Valider toutes les notes Brouillon",
                   command=self._valider_notes).grid(row=0, column=7, padx=6)

        self.arbre_notes = ttk.Treeview(onglet, columns=("eleve", "valeur", "statut"), show="headings", height=12)
        self.arbre_notes.heading("eleve", text="Élève")
        self.arbre_notes.heading("valeur", text="Note /20")
        self.arbre_notes.heading("statut", text="Statut")
        self.arbre_notes.column("eleve", width=220)
        self.arbre_notes.column("valeur", width=80, anchor="center")
        self.arbre_notes.column("statut", width=100, anchor="center")
        self.arbre_notes.pack(fill="both", expand=True)

        self._rafraichir_combos_notes()

    def _rafraichir_combos_notes(self) -> None:
        self.combo_notes_classe["values"] = [c.nom for c in self.gr.classes]
        self.combo_notes_matiere["values"] = [m.nom for m in self.gr.matieres]

    def _afficher_notes(self) -> None:
        classe = self.gr.trouver_classe(self.var_notes_classe.get())
        matiere = self.gr.trouver_matiere(self.var_notes_matiere.get())
        for ligne in self.arbre_notes.get_children():
            self.arbre_notes.delete(ligne)
        if not (classe and matiere):
            return
        trimestre = self.gr.annee_scolaire.trimestre(int(self.var_notes_trimestre.get()))
        for note in trimestre.notes:
            if note.matiere == matiere and note.eleve.classe == classe:
                self.arbre_notes.insert("", "end", values=(note.eleve.nom_complet(), note.valeur, note.statut.value))

    def _valider_notes(self) -> None:
        classe = self.gr.trouver_classe(self.var_notes_classe.get())
        matiere = self.gr.trouver_matiere(self.var_notes_matiere.get())
        if not (classe and matiere):
            messagebox.showwarning("Validation", "Veuillez sélectionner une classe et une matière.")
            return
        nb = self.gr.valider_notes(classe, matiere, int(self.var_notes_trimestre.get()))
        messagebox.showinfo("Validation", f"{nb} note(s) validée(s) et verrouillée(s).")
        self._afficher_notes()

    # ===================== Onglet BULLETINS ===================== #
    def _onglet_bulletins(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Bulletins")

        selection = ttk.Frame(onglet)
        selection.pack(fill="x", pady=(0, 10))
        self.var_bul_classe = tk.StringVar()
        self.var_bul_eleve = tk.StringVar()
        self.var_bul_trimestre = tk.StringVar(value="1")
        self.combo_bul_classe = ttk.Combobox(selection, textvariable=self.var_bul_classe,
                                              width=14, state="readonly")
        self.combo_bul_classe.bind("<<ComboboxSelected>>", lambda _e: self._maj_combo_bul_eleves())
        self.combo_bul_eleve = ttk.Combobox(selection, textvariable=self.var_bul_eleve,
                                             width=22, state="readonly")
        ttk.Label(selection, text="Classe").grid(row=0, column=0, sticky="w")
        self.combo_bul_classe.grid(row=0, column=1, padx=4)
        ttk.Label(selection, text="Élève").grid(row=0, column=2, sticky="w")
        self.combo_bul_eleve.grid(row=0, column=3, padx=4)
        ttk.Label(selection, text="Trimestre").grid(row=0, column=4, sticky="w")
        ttk.Combobox(selection, textvariable=self.var_bul_trimestre, values=("1", "2", "3"),
                     width=4, state="readonly").grid(row=0, column=5, padx=4)
        ttk.Button(selection, text="Générer le bulletin", command=self._generer_bulletin).grid(row=0, column=6, padx=6)

        ttk.Label(onglet, text="Le bulletin du 3e trimestre inclut automatiquement\n"
                               "les résultats annuels (moyenne, rang, mention, décision de passage).",
                  foreground="#666666").pack(anchor="w", pady=(6, 0))

        self._rafraichir_combos_bulletins()

    def _rafraichir_combos_bulletins(self) -> None:
        self.combo_bul_classe["values"] = [c.nom for c in self.gr.classes]

    def _maj_combo_bul_eleves(self) -> None:
        classe = self.gr.trouver_classe(self.var_bul_classe.get())
        self.combo_bul_eleve["values"] = [e.nom_complet() for e in classe.eleves] if classe else []

    def _generer_bulletin(self) -> None:
        classe = self.gr.trouver_classe(self.var_bul_classe.get())
        if not classe:
            messagebox.showwarning("Bulletin", "Veuillez sélectionner une classe.")
            return
        eleve = next((e for e in classe.eleves if e.nom_complet() == self.var_bul_eleve.get()), None)
        if not eleve:
            messagebox.showwarning("Bulletin", "Veuillez sélectionner un élève.")
            return
        bulletin = self.app.generateur_bulletin.generer(eleve, classe, int(self.var_bul_trimestre.get()))
        FenetreBulletin(self, bulletin)

    # ===================== Onglet STATISTIQUES ===================== #
    def _onglet_statistiques(self) -> None:
        onglet = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(onglet, text="Statistiques")

        selection = ttk.Frame(onglet)
        selection.pack(fill="x", pady=(0, 10))
        self.var_stats_classe = tk.StringVar()
        self.var_stats_trimestre = tk.StringVar(value="1")
        self.combo_stats_classe = ttk.Combobox(selection, textvariable=self.var_stats_classe,
                                                width=14, state="readonly")
        ttk.Label(selection, text="Classe").grid(row=0, column=0, sticky="w")
        self.combo_stats_classe.grid(row=0, column=1, padx=4)
        ttk.Label(selection, text="Trimestre").grid(row=0, column=2, sticky="w")
        ttk.Combobox(selection, textvariable=self.var_stats_trimestre, values=("1", "2", "3"),
                     width=4, state="readonly").grid(row=0, column=3, padx=4)
        ttk.Button(selection, text="Analyser", command=self._analyser).grid(row=0, column=4, padx=6)

        self.cadre_resume = ttk.Frame(onglet)
        self.cadre_resume.pack(fill="x", pady=(0, 10))

        self.cadre_graphiques = ttk.Frame(onglet)
        self.cadre_graphiques.pack(fill="both", expand=True)

        self._rafraichir_combos_stats()

    def _rafraichir_combos_stats(self) -> None:
        self.combo_stats_classe["values"] = [c.nom for c in self.gr.classes]

    def _analyser(self) -> None:
        classe = self.gr.trouver_classe(self.var_stats_classe.get())
        if not classe:
            messagebox.showwarning("Statistiques", "Veuillez sélectionner une classe.")
            return
        trimestre_numero = int(self.var_stats_trimestre.get())
        analyseur = self.app.analyseur_statistique

        for widget in self.cadre_resume.winfo_children():
            widget.destroy()
        for widget in self.cadre_graphiques.winfo_children():
            widget.destroy()

        moyenne_classe = analyseur.moyenne_classe(classe, trimestre_numero)
        taux = analyseur.taux_reussite_annuel(classe)
        meilleure = analyseur.meilleure_moyenne(classe, trimestre_numero)
        plus_faible = analyseur.plus_faible_moyenne(classe, trimestre_numero)

        textes = [
            ("Moyenne de la classe", f"{moyenne_classe:.2f} / 20" if moyenne_classe is not None else "—"),
            ("Taux de réussite annuel", f"{taux:.1f} %" if taux is not None else "—"),
            ("Meilleure moyenne", f"{meilleure[1]:.2f} ({meilleure[0].nom_complet()})" if meilleure else "—"),
            ("Plus faible moyenne", f"{plus_faible[1]:.2f} ({plus_faible[0].nom_complet()})" if plus_faible else "—"),
        ]
        for libelle, valeur in textes:
            carte = ttk.LabelFrame(self.cadre_resume, text=libelle, padding=8)
            carte.pack(side="left", expand=True, fill="x", padx=4)
            ttk.Label(carte, text=valeur, font=("Segoe UI", 10, "bold")).pack()

        repartition = analyseur.repartition_mentions(classe, trimestre_numero)
        GraphiqueCamembert(self.cadre_graphiques, repartition,
                            titre="Répartition des mentions").pack(side="left", padx=8, pady=8)

        classement = analyseur.classement(classe, trimestre_numero)
        moyennes_par_eleve = {f"{e.prenom[0]}.{e.nom}": m for _, e, m in classement[:6]}
        GraphiqueBarres(self.cadre_graphiques, moyennes_par_eleve,
                         titre="Moyennes (6 premiers)").pack(side="left", padx=8, pady=8)
