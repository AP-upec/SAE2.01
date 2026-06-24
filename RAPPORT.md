# Rapport — SAE 2.01

**Application web « Données de santé libérale »**
Équipe : Gimenez · De Sousa · Piscitello — BUT Informatique, IUT de Créteil-Vitry

## 1. Cahier des charges

L'objectif est de transformer la base de données de dimensions construite en
SAE 2.04 en une application web utilisable. L'utilisateur doit pouvoir :

- choisir une profession de santé et un territoire (région / département) ;
- consulter les effectifs, densités, honoraires et prescriptions correspondants ;
- visualiser ces données sous forme de tableaux, de graphiques et d'une carte ;
- comparer deux territoires.

Les listes déroulantes sont alimentées par la base MySQL (sans appel réseau) ;
les valeurs chiffrées sont récupérées en temps réel via l'API data.ameli.fr.

## 2. Choix techniques

- **Flask** (Python) avec une architecture **MVC** et des **blueprints** (un par page).
- **SQLAlchemy** pour l'accès à la base MySQL (modèles réutilisés de la SAE 2.04).
- **Jinja2** pour les templates (héritage d'un gabarit commun `base.html`).
- **Chart.js** pour les graphiques, **Leaflet** pour la carte.
- Une classe **`AmeliAPI`** centralise tous les appels à l'API et gère un cache
  en mémoire ainsi que les erreurs réseau.

## 3. Fonctionnalités réalisées

**Socle (minimum attendu)**
- Page d'accueil avec formulaire de sélection.
- Cascade région → département en AJAX.
- Tableau des effectifs et densités.
- Graphique d'évolution (Chart.js).
- Gestion des erreurs (page 404, API indisponible).

**Fonctionnalités avancées**
- Page honoraires (avec type d'honoraires).
- Page prescriptions (postes de prescription).
- Comparaison de deux départements.
- Mise en cache des appels API.
- Export CSV de l'évolution des effectifs.
- Authentification administrateur (statistiques).

**Ouverture**
- Carte interactive des densités par département (Leaflet).
- Tests automatisés (pytest) : unitaires (`AmeliAPI`) et d'intégration (routes).
- Déploiement sur Alwaysdata, avec mise à jour automatique depuis GitHub.

## 4. Difficultés rencontrées et solutions

- **Page honoraires** : la méthode d'accès à l'API visait le mauvais jeu de
  données et recevait ses paramètres dans le désordre. Réécriture de la méthode
  et alignement entre le contrôleur et le service.
- **Doublons** dans le menu des types d'honoraires : déduplication directement
  dans la requête à la base.
- **Mise en production** : une erreur dans l'adresse du serveur de base de
  données provoquait une erreur 500 ; correction de la configuration du site.
- **Sous-dossier de déploiement** (`/sae201_b1`) : l'application devait tenir
  compte de ce préfixe, à la fois côté serveur (routage) et côté JavaScript
  (appels `fetch`), sinon les pages renvoyaient des erreurs 404.

## 5. Améliorations possibles

- Export PDF en plus du CSV.
- Tableau de bord regroupant plusieurs indicateurs.
- Couverture de tests étendue et données mises en cache plus longtemps.

## 6. Répartition du travail

| Membre | Contributions principales |
|---|---|
| Gimenez | _à compléter_ |
| De Sousa | _à compléter_ |
| Piscitello | _à compléter_ |
