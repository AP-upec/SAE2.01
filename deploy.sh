#!/usr/bin/env bash
# Deploiement du site sur Alwaysdata.
# Cette logique est aussi recopiee dans la tache planifiee du compte sae204
# (Avance > Taches planifiees), qui l'execute toutes les 5 minutes.
# Met a jour le code depuis GitHub (main) et recharge l'app uWSGI si besoin.
# Le rechargement passe par touch-reload (parametre uWSGI du site, sur wsgi.py),
# donc aucun token ni secret n'est necessaire ici.
set -u
cd "$(cd "$(dirname "$0")" && pwd)" || exit 1
REPO="https://github.com/AP-upec/SAE2.01.git"

# Initialiser le depot si le dossier n'en est pas un (1er deploiement)
if [ ! -d .git ]; then
    git init -q
    git remote add origin "$REPO" 2>/dev/null || git remote set-url origin "$REPO"
fi

git fetch -q origin main || exit 1
OLD="$(git rev-parse HEAD 2>/dev/null || true)"
git reset -q --hard origin/main
NEW="$(git rev-parse HEAD)"

# Rien de nouveau -> on s'arrete (pas de rechargement inutile)
[ "$OLD" = "$NEW" ] && { echo "deploy: deja a jour ($NEW)"; exit 0; }
echo "deploy: $OLD -> $NEW"

# Dependances seulement si requirements.txt a change (venv du site)
if git diff --name-only "$OLD" "$NEW" 2>/dev/null | grep -q '^requirements.txt$'; then
    [ -x venv/bin/pip ] && venv/bin/pip install -q -r requirements.txt
fi

# Recharger l'app : touch du fichier surveille par uWSGI (touch-reload)
touch wsgi.py
echo "deploy: termine, app rechargee"
