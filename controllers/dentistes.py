from flask import Blueprint, render_template
from models.dimensions import Departement
from models.db import Session
from services.ameli_api import AmeliAPI

bp = Blueprint("dentistes", __name__, url_prefix="/dentistes")

@bp.route("/")
def carte_dentistes():
    api = AmeliAPI()
    session = Session()

    PROFESSION_DENTISTE = 4
    ANNEE = 2023

    donnees = []
    for dept in session.query(Departement).all():
        effectif = api.get_effectifs(PROFESSION_DENTISTE, dept.code, ANNEE)
        donnees.append({
            "code": dept.code,
            "libelle": dept.libelle,
            "effectif": effectif or 0
        })

    session.close()
    return render_template("carte_dentistes.html", donnees=donnees)
