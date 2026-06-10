from flask import Blueprint, render_template, request

from models.db import Session
from models.dimensions import Departement, ProfessionSante, Region
from services.ameli_api import AmeliAPI

bp_comparaison = Blueprint("comparaison", __name__, url_prefix="/comparaison")
api = AmeliAPI()

ANNEES = list(range(2024, 2009, -1))


def _departements_de_region(session, region_id):
    if not region_id:
        return []

    return (session.query(Departement)
            .filter_by(region_id=region_id)
            .order_by(Departement.code).all())


def _ligne_resultat(profession, departement, annee):
    donnees = api.get_effectifs(profession.libelle, departement.code, annee)
    if not donnees:
        return None

    return donnees[0]


@bp_comparaison.route("")
@bp_comparaison.route("/")
def afficher():
    """Compare deux départements pour une profession et une année."""
    profession_id = request.args.get("profession_id", type=int)
    annee = request.args.get("annee", type=int)
    region_1_id = request.args.get("region_1_id", type=int)
    departement_1_id = request.args.get("departement_1_id", type=int)
    region_2_id = request.args.get("region_2_id", type=int)
    departement_2_id = request.args.get("departement_2_id", type=int)

    session = Session()
    try:
        regions = session.query(Region).order_by(Region.libelle).all()
        professions = (session.query(ProfessionSante)
                       .order_by(ProfessionSante.libelle).all())

        profession = session.get(ProfessionSante, profession_id) if profession_id else None
        departement_1 = session.get(Departement, departement_1_id) if departement_1_id else None
        departement_2 = session.get(Departement, departement_2_id) if departement_2_id else None

        if departement_1:
            region_1_id = departement_1.region_id
        if departement_2:
            region_2_id = departement_2.region_id

        departements_1 = _departements_de_region(session, region_1_id)
        departements_2 = _departements_de_region(session, region_2_id)

        comparaison = None
        evolution_1 = []
        evolution_2 = []
        message = None

        if profession and departement_1 and departement_2 and annee:
            if departement_1.id == departement_2.id:
                message = "Choisissez deux départements différents pour les comparer."
            else:
                comparaison = [
                    {
                        "departement": departement_1,
                        "resultat": _ligne_resultat(profession, departement_1, annee),
                        "couleur": "#0474ba",
                    },
                    {
                        "departement": departement_2,
                        "resultat": _ligne_resultat(profession, departement_2, annee),
                        "couleur": "#f17720",
                    },
                ]
                evolution_1 = api.get_evolution_effectifs(profession.libelle, departement_1.code)
                evolution_2 = api.get_evolution_effectifs(profession.libelle, departement_2.code)

        return render_template(
            "comparaison.html",
            regions=regions,
            professions=professions,
            annees=ANNEES,
            region_1_id=region_1_id,
            region_2_id=region_2_id,
            departements_1=departements_1,
            departements_2=departements_2,
            departement_1=departement_1,
            departement_2=departement_2,
            profession=profession,
            annee=annee,
            comparaison=comparaison,
            evolution_1=evolution_1,
            evolution_2=evolution_2,
            message=message,
        )
    finally:
        session.close()
