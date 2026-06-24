import os
from flask import Flask, render_template
from config import Config

from controllers.accueil import bp_accueil
from controllers.api import bp_api
from controllers.prescriptions import bp_prescriptions
from controllers.comparaison import bp_comparaison
from controllers.honoraires import bp_honoraires
from controllers.auth import bp_auth
from controllers.dentistes import bp as dentistes_bp
from controllers.export import bp_export

app = Flask(__name__)
app.config.from_object(Config)


class _PrefixMiddleware:
    """Sert l'application sous un sous-chemin (ex: /sae201_b1) en production.
    Alwaysdata transmet le sous-chemin dans l'URL sans le retirer : on le déplace
    de PATH_INFO vers SCRIPT_NAME pour que le routage et url_for restent corrects.
    Inactif en local (APP_BASE_URL non défini)."""

    def __init__(self, wsgi_app, prefix):
        self.wsgi_app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path == self.prefix or path.startswith(self.prefix + "/"):
            environ["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "") + self.prefix
            environ["PATH_INFO"] = path[len(self.prefix):] or "/"
        return self.wsgi_app(environ, start_response)


_prefix = os.getenv("APP_BASE_URL", "").rstrip("/")
if _prefix:
    app.wsgi_app = _PrefixMiddleware(app.wsgi_app, _prefix)

# Enregistrement des blueprints
app.register_blueprint(bp_accueil)
app.register_blueprint(bp_api)
app.register_blueprint(bp_prescriptions)
app.register_blueprint(bp_comparaison)
app.register_blueprint(bp_honoraires)
app.register_blueprint(bp_auth)
app.register_blueprint(dentistes_bp)
app.register_blueprint(bp_export)

# Gestion des erreurs
@app.errorhandler(404)
def page_non_trouvee(e):
    return render_template("erreur.html", message="Page non trouvée."), 404

@app.errorhandler(500)
def erreur_serveur(e):
    return render_template("erreur.html", message="Erreur interne. Réessayez plus tard."), 500

if __name__ == "__main__":
    app.run(debug=True)
