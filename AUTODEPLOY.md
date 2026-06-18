# Déploiement automatique (Alwaysdata)

À chaque push sur `main`, une tâche planifiée du compte Alwaysdata `sae204`
récupère le code et recharge le site — toutes les **5 minutes**.

## Comment ça marche
- Le dossier du site `/home/sae204/www/sae201_b1` est un clone git de `main`.
- Une **tâche planifiée** (panneau → Avancé → Tâches planifiées, « Deploiement
  auto depuis GitHub ») exécute toutes les 5 min la logique de `deploy.sh` :
  `git fetch` + `git reset --hard origin/main`, réinstalle les dépendances si
  `requirements.txt` a changé, puis `touch wsgi.py`.
- Le site a le paramètre uWSGI **`touch-reload = .../wsgi.py`** : toucher
  `wsgi.py` recharge l'application → pas besoin de token API ni de secret.
- Le dépôt est public → `git pull` anonyme : aucun secret, aucun webhook,
  aucun droit admin GitHub requis.

> Ce n'est pas instantané (polling toutes les 5 min). Un vrai webhook « à chaque
> push » exigerait les droits **admin** du dépôt GitHub, que l'équipe n'a pas.

## Points de config importants (déjà en place)
- **Variables d'environnement du site** (Web → Sites → config) : `DB_USER`,
  `DB_PASSWORD`, `DB_HOST=mysql-sae204.alwaysdata.net`, `DB_NAME`, `SECRET_KEY`,
  `APP_BASE_URL=/sae201_b1`.
- **Sous-chemin `/sae201_b1`** : le site est servi sous un sous-dossier. `app.py`
  lit `APP_BASE_URL` et déplace le préfixe de l'URL via un petit middleware WSGI
  (sinon toutes les routes renvoient 404 en prod). Inactif en local.
- **`touch-reload`** dans les paramètres uWSGI du site.

## Vérifier
Pousser un commit sur `main`, attendre ≤ 5 min, recharger
`https://sae204.alwaysdata.net/sae201_b1/`. Logs : panneau → la tâche → Logs.

## Déploiement manuel (au besoin)
En SSH sur le compte : `bash /home/sae204/www/sae201_b1/deploy.sh`.
