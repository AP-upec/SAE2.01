# SAE 2.01 — Données de santé libérale

Application web (Flask) qui permet d'explorer les données des professionnels de
santé libéraux par territoire : on choisit une profession et un département, et
l'application affiche les effectifs, densités, honoraires et prescriptions
correspondants, sous forme de tableaux, de graphiques et d'une carte.

Les listes (régions, départements, professions…) viennent de la base de la
SAE 2.04 ; les valeurs chiffrées sont récupérées en temps réel via l'API
publique [data.ameli.fr](https://data.ameli.fr).

- **Équipe :** Gimenez · De Sousa · Piscitello
- **Démo en ligne :** https://sae204.alwaysdata.net/sae201_b1/

## Fonctionnalités

- **Accueil** : sélection profession / région / département / année, avec mise à
  jour automatique des départements selon la région (AJAX), tableau des effectifs
  et densités, et graphique d'évolution.
- **Prescriptions** : postes de prescription par profession, département et année.
- **Honoraires** : montants par type d'honoraires.
- **Comparaison** : deux territoires comparés côte à côte (graphiques superposés).
- **Carte des densités** : carte interactive de France (Leaflet) colorée par
  densité, avec choix de la profession et de l'année.
- **Export CSV** : téléchargement de l'évolution des effectifs.
- **Espace administrateur** : connexion et statistiques (`/admin`).
- **Cache** des appels à l'API pour accélérer l'affichage.

## Prérequis

- Python 3.10 ou supérieur
- Accès à la base MySQL de la SAE 2.04

## Installation

```bash
git clone https://github.com/AP-upec/SAE2.01.git
cd SAE2.01
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example.txt .env         # puis remplir les identifiants de la base
```

## Lancement

```bash
python app.py
```

L'application est accessible sur http://localhost:5000.

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## Captures d'écran

| Accueil (effectifs + graphique) | Carte des densités | Comparaison |
|---|---|---|
| ![Accueil](docs/img/accueil.png) | ![Carte](docs/img/carte.png) | ![Comparaison](docs/img/comparaison.png) |

## Architecture (MVC)

```
app.py            point d'entrée Flask + enregistrement des blueprints
config.py         configuration (lecture du .env)
wsgi.py           point d'entrée WSGI (déploiement)
models/           accès aux données : db.py (SQLAlchemy) + dimensions.py (ORM)
services/         ameli_api.py : accès centralisé à l'API data.ameli.fr (+ cache)
controllers/      un blueprint par page (accueil, prescriptions, honoraires,
                  comparaison, dentistes/carte, export, api, auth)
templates/        vues HTML Jinja2 (héritage de base.html)
static/           CSS, JavaScript, GeoJSON
tests/            tests pytest (unitaires + intégration)
```

## Déploiement

L'application est déployée sur Alwaysdata. La procédure et le déploiement
automatique sont décrits dans [AUTODEPLOY.md](AUTODEPLOY.md).
