from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import Region, ProfessionSante, Departement
from services.ameli_api import AmeliAPI
bp_accueil = Blueprint("accueil", __name__)
api = AmeliAPI()
# Années disponibles dans le dataset ameli (de la plus récente à la plus ancienne)
ANNEES = list(range(2024, 2009, -1))
@bp_accueil.route("/")
def afficher():
    """Affiche le formulaire de sélection et, si la sélection est complète,
    les effectifs correspondants."""
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)
    annee = request.args.get("annee", type=int)
    session = Session()
    try:
        # Données pour alimenter le formulaire
        regions = session.query(Region).order_by(Region.libelle).all()
        professions = (session.query(ProfessionSante)
                       .order_by(ProfessionSante.libelle).all())
        prof = session.get(ProfessionSante, profession_id) if profession_id else None
        dept = session.get(Departement, departement_id) if departement_id else None
        # Départements de la région du département choisi : permet de réafficher
        # correctement la liste déroulante après soumission (sans attendre le JS).
        region_id = dept.region_id if dept else None
        departements = ((session.query(Departement)
                         .filter_by(region_id=region_id)
                         .order_by(Departement.code).all()) if region_id else [])
        # Résultats uniquement si la sélection est complète
        resultats = evolution = None
        if prof and dept and annee:
            resultats = api.get_effectifs(prof.libelle, dept.code, annee)
            evolution = api.get_evolution_effectifs(prof.libelle, dept.code)
        return render_template(
            "accueil.html",
            regions=regions, professions=professions, annees=ANNEES,
            departements=departements, region_id=region_id,
            prof=prof, dept=dept, annee=annee,
            resultats=resultats, evolution=evolution or [],
        )
    finally:
        session.close()
