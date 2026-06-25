"""Tests d'intégration des routes Flask (base SQLite en mémoire).

Les routes sont testées sans sélection complète, pour ne pas dépendre de l'API
ameli.fr ; la seule route qui appelle l'API (carte des densités) est testée avec
un faux service.
"""
import models.db as db
from models.dimensions import Region, ProfessionSante, Departement


def _id_region(code):
    s = db.Session()
    try:
        return s.query(Region).filter_by(code=code).first().id
    finally:
        s.close()


def _id_profession(libelle):
    s = db.Session()
    try:
        return s.query(ProfessionSante).filter_by(libelle=libelle).first().id
    finally:
        s.close()


def _id_departement(code):
    s = db.Session()
    try:
        return s.query(Departement).filter_by(code=code).first().id
    finally:
        s.close()


def test_accueil_repond(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'name="profession_id"' in r.get_data(as_text=True)


def test_page_inconnue_404(client):
    r = client.get("/cette-page-nexiste-pas")
    assert r.status_code == 404
    assert "erreur" in r.get_data(as_text=True).lower()


def test_api_departements_json(client):
    rid = _id_region("11")  # Île-de-France
    r = client.get(f"/api/departements/{rid}")
    assert r.status_code == 200
    codes = [d["code"] for d in r.get_json()]
    assert "75" in codes and "77" in codes
    assert "69" not in codes  # le 69 est dans une autre région


def test_honoraires_menu_sans_doublon(client):
    """Le menu des types d'honoraires ne doit lister chaque niveau 1 qu'une fois."""
    r = client.get("/honoraires")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    # 2 types ont niveau_1="Actes" en base, mais le menu doit n'en afficher qu'un
    assert html.count(">Actes<") == 1
    assert ">Dépassements<" in html
    assert ">Rémunérations forfaitaires<" in html


def test_prescriptions_repond(client):
    assert client.get("/prescriptions").status_code == 200


def test_comparaison_repond(client):
    assert client.get("/comparaison/").status_code == 200


def test_carte_page_repond(client):
    r = client.get("/dentistes/")
    assert r.status_code == 200
    assert "Ensemble des médecins" in r.get_data(as_text=True)


def test_carte_densites_json(client, monkeypatch):
    import controllers.dentistes as dent
    monkeypatch.setattr(
        dent.api, "get_effectifs_par_departement",
        lambda profession, annee: {"75": {"effectif": 100, "densite": 50.0}},
    )
    pid = _id_profession("Ensemble des médecins")
    r = client.get(f"/dentistes/densites?profession_id={pid}&annee=2023")
    assert r.status_code == 200
    data = r.get_json()
    assert data["annee"] == 2023
    assert data["departements"]["75"]["densite"] == 50.0


def test_admin_protege_redirige_vers_login(client):
    r = client.get("/admin/")
    assert r.status_code == 302
    assert "/admin/login" in r.headers["Location"]


def test_admin_login_accessible(client):
    assert client.get("/admin/login").status_code == 200


def test_prefix_middleware():
    """Le middleware déplace le sous-chemin de PATH_INFO vers SCRIPT_NAME."""
    from app import _PrefixMiddleware
    vu = {}

    def fausse_app(environ, start_response):
        vu["PATH_INFO"] = environ["PATH_INFO"]
        vu["SCRIPT_NAME"] = environ.get("SCRIPT_NAME", "")
        return []

    mw = _PrefixMiddleware(fausse_app, "/sae201_b1")

    mw({"PATH_INFO": "/sae201_b1/honoraires", "SCRIPT_NAME": ""}, lambda *a: None)
    assert vu["PATH_INFO"] == "/honoraires"
    assert vu["SCRIPT_NAME"] == "/sae201_b1"

    mw({"PATH_INFO": "/sae201_b1", "SCRIPT_NAME": ""}, lambda *a: None)
    assert vu["PATH_INFO"] == "/"

    mw({"PATH_INFO": "/autre", "SCRIPT_NAME": ""}, lambda *a: None)
    assert vu["PATH_INFO"] == "/autre"
    assert vu["SCRIPT_NAME"] == ""


def test_export_csv(client, monkeypatch):
    import controllers.export as exp
    monkeypatch.setattr(
        exp.api, "get_evolution_effectifs",
        lambda profession, code: [
            {"annee": "2022", "effectif": 10, "densite": 1.5},
            {"annee": "2023", "effectif": 12, "densite": 1.8},
        ],
    )
    s = db.Session()
    try:
        from models.dimensions import Departement
        dept_id = s.query(Departement).filter_by(code="75").first().id
    finally:
        s.close()
    pid = _id_profession("Ensemble des médecins")

    r = client.get(f"/export/effectifs.csv?profession_id={pid}&departement_id={dept_id}")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    assert "attachment" in r.headers.get("Content-Disposition", "")
    corps = r.get_data(as_text=True)
    assert "Annee,Effectif,Densite" in corps
    assert "2023,12,1.8" in corps


def test_export_honoraires_csv(client, monkeypatch):
    import controllers.export as exp
    monkeypatch.setattr(exp.api, "get_honoraires", lambda *a, **k: [
        {"type_honoraires_niveau_1": "Actes", "type_honoraires_niveau_2": None,
         "type_honoraires_niveau_3": None, "montant_honoraires": 100,
         "montant_honoraires_moyens": 5}])
    pid = _id_profession("Cardiologues")
    did = _id_departement("75")
    r = client.get(f"/export/honoraires.csv?profession_id={pid}&departement_id={did}&annee=2023")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    corps = r.get_data(as_text=True)
    assert "Type niveau 1" in corps and "Actes" in corps


def test_export_prescriptions_csv(client, monkeypatch):
    import controllers.export as exp
    monkeypatch.setattr(exp.api, "get_prescriptions", lambda *a, **k: [
        {"libelle_poste_prescription": "Médicaments",
         "montant_total_prescription": 10, "montant_moyen_prescription": 2}])
    pid = _id_profession("Cardiologues")
    did = _id_departement("75")
    r = client.get(f"/export/prescriptions.csv?profession_id={pid}&departement_id={did}&annee=2023")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    assert "Médicaments" in r.get_data(as_text=True)


def test_export_comparaison_csv(client, monkeypatch):
    import controllers.export as exp
    monkeypatch.setattr(exp.api, "get_evolution_effectifs",
                        lambda profession, code: [{"annee": "2023", "effectif": 5, "densite": 1.0}])
    pid = _id_profession("Cardiologues")
    r = client.get(f"/export/comparaison.csv?profession_id={pid}"
                   f"&departement_1_id={_id_departement('75')}"
                   f"&departement_2_id={_id_departement('77')}")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    assert "Departement,Annee,Effectif,Densite" in r.get_data(as_text=True)


def test_export_densites_csv(client, monkeypatch):
    import controllers.export as exp
    monkeypatch.setattr(exp.api, "get_effectifs_par_departement",
                        lambda profession, annee: {"75": {"effectif": 100, "densite": 50.0}})
    pid = _id_profession("Ensemble des médecins")
    r = client.get(f"/export/densites.csv?profession_id={pid}&annee=2023")
    assert r.status_code == 200
    assert "text/csv" in r.headers["Content-Type"]
    assert "75,100,50.0" in r.get_data(as_text=True)
