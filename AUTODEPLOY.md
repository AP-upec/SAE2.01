# Déploiement automatique (Alwaysdata)

À chaque push sur `main`, le code part sur GitHub. Une tâche planifiée du compte
Alwaysdata vérifie le dépôt toutes les 5 minutes et, s'il y a du nouveau, met le
site à jour et le redémarre. Tout passe par `deploy.sh` (aucun secret dedans : le
dépôt est public).

> Pourquoi pas un vrai webhook « à chaque push » ? Il faudrait être admin du dépôt
> GitHub (secrets / webhooks), ce qui n'est pas notre cas. Le polling toutes les
> 5 min est la seule solution dans notre périmètre.

## Mise en place (une seule fois, sur le compte Alwaysdata)

1. **Le dossier du site doit être un clone git de `main`.** En SSH :
   ```
   cd ~/www
   git clone https://github.com/AP-upec/SAE2.01.git sae201_b1   # si pas déjà fait
   ```

2. **Token API + id du site.**
   - Panneau Alwaysdata → *Profil → Tokens* (la 2FA doit être activée) → générer un token.
   - Récupérer l'id du site : *Web → Sites*, ou
     `curl --basic --user "TOKEN account=sae204:" https://api.alwaysdata.com/v1/site/`

3. **Fichier d'identifiants hors dépôt** `~/.adata.env` (jamais commité) :
   ```
   ADATA_API_KEY=le_token
   ADATA_SITE_ID=l_id_du_site
   ```
   ```
   chmod 600 ~/.adata.env
   ```

4. **Test manuel :**
   ```
   chmod +x ~/www/sae201_b1/deploy.sh
   source ~/.adata.env && bash ~/www/sae201_b1/deploy.sh
   ```
   On doit voir le pull, puis `restart API -> HTTP 204`.

5. **Tâche planifiée :** panneau → *Avancé → Tâches planifiées* → ajouter
   une commande :
   ```
   source ~/.adata.env && bash ~/www/sae201_b1/deploy.sh
   ```
   fréquence `*/5 * * * *`, répertoire de travail `~/www/sae201_b1`, e-mail
   d'erreur renseigné.

## Vérifier

Pousser un commit sur `main`, attendre ≤ 5 min, recharger
`https://sae204.alwaysdata.net/sae201_b1/`. Logs des tâches dans
`~/admin/logs/jobs/`.
