"""Service central : registre de toutes les données et opérations CRUD."""

from __future__ import annotations
import itertools
import pickle
from pathlib import Path
from typing import List, Optional

from models import (
    Eleve, Enseignant, Classe, Matiere, Affectation,
    Utilisateur, RoleUtilisateur, Note, AnneeScolaire,
)


class GestionnaireResultats:
    """Point d'entrée unique vers les données de l'application.

    Tient les collections principales (élèves, classes, matières,
    enseignants, affectations, utilisateurs) et l'année scolaire en cours,
    et fournit les opérations CRUD ainsi que la persistance sur disque.
    """

    def __init__(self, annee_scolaire: Optional[AnneeScolaire] = None):
        self.annee_scolaire = annee_scolaire or AnneeScolaire("2025-2026")
        self.eleves: List[Eleve] = []
        self.classes: List[Classe] = []
        self.matieres: List[Matiere] = []
        self.enseignants: List[Enseignant] = []
        self.affectations: List[Affectation] = []
        self.utilisateurs: List[Utilisateur] = []

    # --- Classes ---
    def ajouter_classe(self, classe: Classe) -> None:
        if any(c.nom == classe.nom for c in self.classes):
            raise ValueError(f"La classe {classe.nom} existe déjà.")
        self.classes.append(classe)

    def trouver_classe(self, nom: str) -> Optional[Classe]:
        return next((c for c in self.classes if c.nom == nom), None)

    # --- Matières ---
    def ajouter_matiere(self, matiere: Matiere) -> None:
        if matiere in self.matieres:
            raise ValueError(f"La matière {matiere.nom} existe déjà.")
        self.matieres.append(matiere)

    def trouver_matiere(self, nom: str) -> Optional[Matiere]:
        return next((m for m in self.matieres if m.nom.lower() == nom.lower()), None)

    # --- Élèves ---
    def ajouter_eleve(self, eleve: Eleve, classe: Classe) -> None:
        if eleve in self.eleves:
            raise ValueError(f"{eleve.nom_complet()} est déjà enregistré.")
        classe.ajouter_eleve(eleve)
        self.eleves.append(eleve)

    def supprimer_eleve(self, eleve: Eleve) -> None:
        if eleve.classe:
            eleve.classe.retirer_eleve(eleve)
        self.eleves.remove(eleve)

    def modifier_eleve(self, eleve: Eleve, *, nom: str | None = None, prenom: str | None = None,
                        date_naissance=None, sexe: str | None = None,
                        nouvelle_classe: Optional[Classe] = None) -> None:
        """Met à jour les informations d'un élève déjà enregistré.

        Les setters de Personne/Eleve valident chaque valeur. Le changement
        de classe (s'il y a lieu) est appliqué en dernier, via retrait de
        l'ancienne classe puis ajout à la nouvelle (relation d'agrégation).
        """
        if nom is not None:
            eleve.nom = nom
        if prenom is not None:
            eleve.prenom = prenom
        if date_naissance is not None:
            eleve.date_naissance = date_naissance
        if sexe is not None:
            eleve.sexe = sexe
        if nouvelle_classe is not None and eleve.classe is not nouvelle_classe:
            if eleve.classe:
                eleve.classe.retirer_eleve(eleve)
            nouvelle_classe.ajouter_eleve(eleve)

    # --- Enseignants ---
    def ajouter_enseignant(self, enseignant: Enseignant) -> None:
        if enseignant in self.enseignants:
            raise ValueError(f"{enseignant.nom_complet()} est déjà enregistré.")
        self.enseignants.append(enseignant)

    # --- Affectations ---
    def affecter(self, enseignant: Enseignant, classe: Classe, matiere: Matiere) -> Affectation:
        affectation = Affectation(enseignant, classe, matiere)
        enseignant.ajouter_affectation(affectation)
        self.affectations.append(affectation)
        return affectation

    def retirer_affectation(self, affectation: Affectation) -> None:
        affectation.enseignant.retirer_affectation(affectation)
        self.affectations.remove(affectation)

    # --- Utilisateurs ---
    def creer_compte_administrateur(self, identifiant: str, mot_de_passe: str) -> Utilisateur:
        utilisateur = Utilisateur(identifiant, mot_de_passe, RoleUtilisateur.ADMINISTRATEUR)
        self.utilisateurs.append(utilisateur)
        return utilisateur

    def creer_compte_enseignant(self, identifiant: str, mot_de_passe: str, enseignant: Enseignant) -> Utilisateur:
        utilisateur = Utilisateur(identifiant, mot_de_passe, RoleUtilisateur.ENSEIGNANT, enseignant=enseignant)
        self.utilisateurs.append(utilisateur)
        return utilisateur

    # --- Notes ---
    def saisir_note(self, eleve: Eleve, matiere: Matiere, trimestre_numero: int, valeur: float) -> Note:
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        existante = next((n for n in trimestre.notes_de(eleve) if n.matiere == matiere), None)
        if existante is not None:
            existante.modifier(valeur)
            return existante
        note = Note(eleve, matiere, trimestre_numero, valeur)
        trimestre.ajouter_note(note)
        return note

    def valider_notes(self, classe: Classe, matiere: Matiere, trimestre_numero: int) -> int:
        """Valide (verrouille) toutes les notes Brouillon de cette classe/matière/trimestre."""
        trimestre = self.annee_scolaire.trimestre(trimestre_numero)
        compteur = 0
        for note in trimestre.notes:
            if note.matiere == matiere and note.eleve.classe == classe and note.est_modifiable():
                note.valider()
                compteur += 1
        return compteur

    # --- Persistance (pickle : conserve le graphe d'objets et ses références) ---
    def sauvegarder(self, chemin: str | Path) -> None:
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        with open(chemin, "wb") as fichier:
            pickle.dump(self, fichier)

    @staticmethod
    def charger(chemin: str | Path) -> "GestionnaireResultats":
        with open(chemin, "rb") as fichier:
            gestionnaire = pickle.load(fichier)
        gestionnaire._resynchroniser_compteurs()
        return gestionnaire

    def _resynchroniser_compteurs(self) -> None:
        """Réaligne les compteurs de matricule/code après un chargement disque.

        Eleve._compteur et Enseignant._compteur sont des itertools.count en
        mémoire : ils repartent de 1 à chaque démarrage du programme. Sans ce
        réajustement, un nouvel élève (ou enseignant) ajouté juste après un
        rechargement de données reçoit un matricule (ou code) déjà utilisé
        (ex. EL0001), ce qui est ensuite refusé comme doublon par
        ajouter_eleve(), même s'il s'agit d'une personne différente.
        """
        def _max_suffixe(valeurs, prefixe: str) -> int:
            meilleur = 0
            for valeur in valeurs:
                if valeur.startswith(prefixe) and valeur[len(prefixe):].isdigit():
                    meilleur = max(meilleur, int(valeur[len(prefixe):]))
            return meilleur

        max_matricule = _max_suffixe((e.matricule for e in self.eleves), "EL")
        Eleve._compteur = itertools.count(max_matricule + 1)

        max_code = _max_suffixe((ens.code for ens in self.enseignants), "ENS")
        Enseignant._compteur = itertools.count(max_code + 1)

    def __repr__(self) -> str:
        return (
            f"GestionnaireResultats(annee={self.annee_scolaire.libelle!r}, "
            f"eleves={len(self.eleves)}, classes={len(self.classes)}, "
            f"enseignants={len(self.enseignants)})"
        )
