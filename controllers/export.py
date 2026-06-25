import csv
import io

from flask import Blueprint, request, Response
from models.db import Session
from models.dimensions import ProfessionSante, Departement, TypeHonoraire
from services.ameli_api import AmeliAPI

bp_export = Blueprint("export", __name__, url_prefix="/export")
api = AmeliAPI()


def _csv(entetes, lignes, nom_fichier):
    """Construit une réponse HTTP CSV téléchargeable."""
    sortie = io.StringIO()
    writeur = csv.writer(sortie)
    writeur.writerow(entetes)
    for ligne in lignes:
        writeur.writerow(ligne)
    return Response(
        sortie.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nom_fichier}"'},
    )


def _incomplet():
    return Response("Sélection incomplète.", status=400, mimetype="text/plain")


@bp_export.route("/effectifs.csv")
def effectifs_csv():
    """Évolution des effectifs d'une profession dans un département (page Accueil)."""
    session = Session()
    try:
        prof = session.get(ProfessionSante, request.args.get("profession_id", type=int))
        dept = session.get(Departement, request.args.get("departement_id", type=int))
        if not prof or not dept:
            return _incomplet()
        lignes = api.get_evolution_effectifs(prof.libelle, dept.code)
    finally:
        session.close()
    return _csv(
        ["Annee", "Effectif", "Densite"],
        [[l.get("annee"), l.get("effectif"), l.get("densite")] for l in lignes],
        f"effectifs_{dept.code}.csv",
    )


@bp_export.route("/honoraires.csv")
def honoraires_csv():
    """Honoraires d'une profession dans un département pour une année."""
    annee = request.args.get("annee", type=int)
    session = Session()
    try:
        prof = session.get(ProfessionSante, request.args.get("profession_id", type=int))
        dept = session.get(Departement, request.args.get("departement_id", type=int))
        honoraire_id = request.args.get("honoraire_id", type=int)
        honor = session.get(TypeHonoraire, honoraire_id) if honoraire_id else None
        if not prof or not dept or not annee:
            return _incomplet()
        lignes = api.get_honoraires(prof.libelle, dept.code, annee,
                                    honor.niveau_1 if honor else None)
    finally:
        session.close()
    return _csv(
        ["Type niveau 1", "Type niveau 2", "Type niveau 3", "Montant total", "Montant moyen"],
        [[l.get("type_honoraires_niveau_1"), l.get("type_honoraires_niveau_2"),
          l.get("type_honoraires_niveau_3"), l.get("montant_honoraires"),
          l.get("montant_honoraires_moyens")] for l in lignes],
        f"honoraires_{dept.code}_{annee}.csv",
    )


@bp_export.route("/prescriptions.csv")
def prescriptions_csv():
    """Postes de prescription d'une profession dans un département pour une année."""
    annee = request.args.get("annee", type=int)
    session = Session()
    try:
        prof = session.get(ProfessionSante, request.args.get("profession_id", type=int))
        dept = session.get(Departement, request.args.get("departement_id", type=int))
        if not prof or not dept or not annee:
            return _incomplet()
        lignes = api.get_prescriptions(prof.libelle, dept.code, annee)
    finally:
        session.close()
    return _csv(
        ["Poste", "Montant total", "Montant moyen"],
        [[l.get("libelle_poste_prescription"), l.get("montant_total_prescription"),
          l.get("montant_moyen_prescription")] for l in lignes],
        f"prescriptions_{dept.code}_{annee}.csv",
    )


@bp_export.route("/comparaison.csv")
def comparaison_csv():
    """Évolution des effectifs de deux départements (page Comparaison)."""
    session = Session()
    try:
        prof = session.get(ProfessionSante, request.args.get("profession_id", type=int))
        dept1 = session.get(Departement, request.args.get("departement_1_id", type=int))
        dept2 = session.get(Departement, request.args.get("departement_2_id", type=int))
        if not prof or not dept1 or not dept2:
            return _incomplet()
        lignes = []
        for dept in (dept1, dept2):
            for l in api.get_evolution_effectifs(prof.libelle, dept.code):
                lignes.append([f"{dept.code} {dept.libelle}", l.get("annee"),
                               l.get("effectif"), l.get("densite")])
    finally:
        session.close()
    return _csv(
        ["Departement", "Annee", "Effectif", "Densite"], lignes,
        f"comparaison_{dept1.code}_{dept2.code}.csv",
    )


@bp_export.route("/densites.csv")
def densites_csv():
    """Densités de tous les départements pour une profession et une année (Carte)."""
    annee = request.args.get("annee", type=int) or 2023
    session = Session()
    try:
        prof = session.get(ProfessionSante, request.args.get("profession_id", type=int))
        if not prof:
            return _incomplet()
        donnees = api.get_effectifs_par_departement(prof.libelle, annee)
    finally:
        session.close()
    lignes = [[code, infos.get("effectif"), infos.get("densite")]
              for code, infos in sorted(donnees.items())]
    return _csv(["Departement", "Effectif", "Densite"], lignes, f"densites_{annee}.csv")
