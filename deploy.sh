#!/usr/bin/env bash
# Deploiement automatique du site sur Alwaysdata.
# Lance par une tache planifiee (cron) du compte sae204 : met a jour le code
# depuis GitHub (branche main) et redemarre le site seulement s'il y a du nouveau.
#
# Aucun secret ici (le depot est public) : la cle API et l'id du site sont lus
# depuis l'environnement, charge depuis ~/.adata.env par la tache cron :
#   ADATA_API_KEY=...      cle API Alwaysdata (Profil > Tokens)
#   ADATA_SITE_ID=...      id numerique du site WSGI
#   ADATA_ACCOUNT=sae204   (optionnel, defaut sae204)
set -euo pipefail

# Se placer dans le dossier du depot (la ou se trouve ce script)
cd "$(dirname "$0")"

BRANCHE="${ADATA_BRANCH:-main}"
COMPTE="${ADATA_ACCOUNT:-sae204}"

# 1) Voir s'il y a du nouveau sur origin/main
git fetch --quiet origin "$BRANCHE"
AVANT="$(git rev-parse HEAD)"
APRES="$(git rev-parse "origin/$BRANCHE")"

if [ "$AVANT" = "$APRES" ]; then
    echo "$(date '+%F %T') deploy: deja a jour ($AVANT)"
    exit 0
fi

echo "$(date '+%F %T') deploy: mise a jour $AVANT -> $APRES"

# 2) Aligner le code sur origin/main (.env et venv sont gitignores -> preserves)
git reset --hard "origin/$BRANCHE"

# 3) Reinstaller les dependances seulement si requirements.txt a change
if git diff --name-only "$AVANT" "$APRES" | grep -q '^requirements.txt$'; then
    PIP="pip"
    [ -x "./venv/bin/pip" ] && PIP="./venv/bin/pip"
    echo "$(date '+%F %T') deploy: requirements.txt modifie -> $PIP install"
    "$PIP" install -r requirements.txt
fi

# 4) Redemarrer le site WSGI via l'API Alwaysdata
if [ -n "${ADATA_API_KEY:-}" ] && [ -n "${ADATA_SITE_ID:-}" ]; then
    code="$(curl -s -o /dev/null -w '%{http_code}' -X POST \
        --basic --user "$ADATA_API_KEY account=$COMPTE:" \
        "https://api.alwaysdata.com/v1/site/$ADATA_SITE_ID/restart/")"
    echo "$(date '+%F %T') deploy: restart API -> HTTP $code"
    [ "$code" = "204" ] || { echo "deploy: echec du redemarrage (HTTP $code)" >&2; exit 1; }
else
    echo "deploy: ADATA_API_KEY/ADATA_SITE_ID absents -> redemarrer le site manuellement" >&2
fi

echo "$(date '+%F %T') deploy: termine"
