# Gestion des résultats scolaires

Application de gestion des résultats scolaires développée en Python (programmation orientée objet), avec interface graphique Tkinter.

Projet réalisé par **OUEDRAOGO Zeïd El Gazeli** et **DAO Cédric**, Master 1 Data Science, UJKZ / IFOAD.

## Présentation

L'application permet à un établissement scolaire de gérer, sur une année scolaire découpée en 3 trimestres :

- les élèves, les classes et les matières (avec coefficients) ;
- les enseignants et leurs affectations (un enseignant peut intervenir sur plusieurs classes et plusieurs matières) ;
- la saisie des notes par trimestre, avec un statut Brouillon / Validée (une note validée est verrouillée et ne peut être modifiée que par un administrateur) ;
- le calcul des moyennes, classements, mentions et statistiques par classe ;
- la génération de bulletins trimestriels, le bulletin du 3e trimestre intégrant en plus la moyenne annuelle, le rang annuel et la décision de passage en classe supérieure (seuil : 10/20) ;
- deux types de comptes avec des droits différents : **Administrateur** (Directeur / Secrétariat, accès complet) et **Enseignant** (accès limité aux classes et matières qui lui sont affectées).

## Architecture (aperçu)

Le code est organisé en trois paquets, dans le dossier `code/` :

- `models/` — les classes métier : `Personne` (classe de base), `Eleve` et `Enseignant` (héritage), `Classe`, `Matiere`, `Affectation`, `Note`, `Trimestre`, `AnneeScolaire`, `Bulletin`, `Utilisateur`. Les relations d'héritage, d'association, d'agrégation et de composition exigées par le cahier des charges sont toutes représentées (par exemple : `Eleve(Personne)` pour l'héritage, `Classe` agrège des `Eleve`, `Bulletin` est composé de `LigneBulletin`).
- `services/` — la logique applicative : authentification (`AuthService`), registre central et persistance (`GestionnaireResultats`), statistiques (`AnalyseurStatistique`), génération de bulletins (`GenerateurBulletin`), jeu de données de démonstration (`donnees_demo`).
- `gui/` — l'interface graphique Tkinter : écran de connexion, tableau de bord Administrateur, tableau de bord Enseignant, fenêtre de bulletin, graphiques (barres et camembert) dessinés sans dépendance externe.

Toutes les classes utilisent l'encapsulation (attributs privés avec `@property`) et valident leurs données (lève une exception en cas de valeur invalide).

## Installation et lancement

Aucune dépendance externe n'est nécessaire : seuls Python 3 et le module standard `tkinter` sont requis.

```bash
cd code
python3 main.py
```

Au premier lancement, l'application démarre avec un jeu de données de démonstration (2 classes, 7 élèves, 2 enseignants, 4 matières, des notes sur les 3 trimestres). Les données sont ensuite sauvegardées automatiquement dans `code/data/donnees.pkl` à la fermeture de la fenêtre, puis rechargées au lancement suivant.

### Comptes de démonstration

| Identifiant | Mot de passe | Rôle |
|---|---|---|
| `secretariat` | `admin1234` | Administrateur |
| `konate` | `prof1234` | Enseignant (Mathématiques, 3ème A et 2nde A) |
| `sawadogo` | `prof1234` | Enseignant (Français et Anglais, 3ème A) |

### Démonstration en ligne de commande

Un script `demo_cli.py` exerce l'ensemble des fonctionnalités sans interface graphique (utile pour vérifier rapidement que tout fonctionne) :

```bash
cd code
python3 demo_cli.py
```

## Choix techniques notables

- **Persistance par `pickle`** plutôt que JSON : le graphe d'objets contient des références croisées (une classe référence ses élèves, un élève référence sa classe, un enseignant référence ses affectations, etc.) que `pickle` sérialise nativement, sans conversion manuelle.
- **Mot de passe haché** (SHA-256) plutôt que stocké en clair dans `Utilisateur`.
- **Verrouillage des notes validées** : `Note.modifier()` lève une exception si la note est validée, sauf si un administrateur force la modification.
- **Graphiques maison** (`gui/chart_widgets.py`) dessinés directement sur un `Canvas` Tkinter, pour ne dépendre d'aucune bibliothèque externe comme matplotlib.

## Documents associés

- `Cahier_des_charges_Gestion_Resultats_Scolaires.docx` — cahier des charges détaillé (besoins, architecture, rôles).
- Rapport descriptif du projet (voir fichier `.docx` correspondant).
