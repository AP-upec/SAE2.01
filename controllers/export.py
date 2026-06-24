import csv
import io

from flask import Blueprint, request, Response
from models.db import Session
from models.dimensions import ProfessionSante, Departement
from services.ameli_api import AmeliAPI

bp_export = Blueprint("export", __name__, url_prefix="/export")
api = AmeliAPI()


@bp_export.route("/effectifs.csv")
def effectifs_csv():
    """Exporte au format CSV l'évolution des effectifs d'une profession
    dans un département (toutes les années disponibles)."""
    profession_id = request.args.get("profession_id", type=int)
    departement_id = request.args.get("departement_id", type=int)

    session = Session()
    try:
        prof = session.get(ProfessionSante, profession_id) if profession_id else None
        dept = session.get(Departement, departement_id) if departement_id else None
        if not prof or not dept:
            return Response("Sélection incomplète.", status=400, mimetype="text/plain")
        lignes = api.get_evolution_effectifs(prof.libelle, dept.code)
    finally:
        session.close()

    sortie = io.StringIO()
    writeur = csv.writer(sortie)
    writeur.writerow(["Annee", "Effectif", "Densite"])
    for ligne in lignes:
        writeur.writerow([ligne.get("annee"), ligne.get("effectif"), ligne.get("densite")])

    nom_fichier = f"effectifs_{dept.code}.csv"
    return Response(
        sortie.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nom_fichier}"'},
    )
