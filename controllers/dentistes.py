from flask import Blueprint, render_template
from models.dimensions import Departement
from models.db import Session
from services.ameli_api import AmeliAPI

bp = Blueprint("dentistes", __name__, url_prefix="/dentistes")

# Profession et année utilisées pour la carte de densité
PROFESSION_DENTISTE = "Ensemble des chirurgiens-dentistes"
ANNEE = 2023


@bp.route("/")
def carte_dentistes():
    api = AmeliAPI()
    session = Session()
    try:
        # Un seul appel groupé (tous les départements) au lieu d'un appel par département
        effectifs = api.get_effectifs_par_departement(PROFESSION_DENTISTE, ANNEE)
        donnees = []
        for dept in session.query(Departement).order_by(Departement.code).all():
            infos = effectifs.get(dept.code, {})
            donnees.append({
                "code": dept.code,
                "libelle": dept.libelle,
                "effectif": infos.get("effectif") or 0,
                "densite": infos.get("densite") or 0,
            })
    finally:
        session.close()
    return render_template("carte_dentistes.html", donnees=donnees, annee=ANNEE)
