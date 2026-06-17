from flask import Blueprint, render_template, request, jsonify
from models.dimensions import ProfessionSante
from models.db import Session
from services.ameli_api import AmeliAPI

bp = Blueprint("dentistes", __name__, url_prefix="/dentistes")
api = AmeliAPI()

# Années disponibles dans le dataset ameli (de la plus récente à la plus ancienne)
ANNEES = list(range(2024, 2009, -1))


@bp.route("/")
def carte_dentistes():
    """Carte interactive des densités de professionnels de santé par département."""
    session = Session()
    try:
        professions = (session.query(ProfessionSante)
                       .order_by(ProfessionSante.libelle).all())
    finally:
        session.close()
    return render_template("carte_dentistes.html",
                           professions=professions, annees=ANNEES)


@bp.route("/densites")
def densites():
    """Densité et effectif de chaque département pour une profession et une année.
    Renvoyé en JSON et consommé par la carte en AJAX (sans recharger la page)."""
    profession_id = request.args.get("profession_id", type=int)
    annee = request.args.get("annee", type=int) or 2023
    session = Session()
    try:
        prof = session.get(ProfessionSante, profession_id) if profession_id else None
        if prof is None:
            prof = (session.query(ProfessionSante)
                    .order_by(ProfessionSante.libelle).first())
        departements = api.get_effectifs_par_departement(prof.libelle, annee)
    finally:
        session.close()
    return jsonify({
        "profession": prof.libelle,
        "annee": annee,
        "departements": departements,
    })
