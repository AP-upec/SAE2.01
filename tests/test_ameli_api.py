"""Tests unitaires de la classe AmeliAPI (sans appel réseau réel).

On remplace la session HTTP de l'objet par un faux objet : on vérifie ainsi
l'URL et les paramètres construits, le parsing, le cache et la gestion d'erreur.
"""
import requests

from services.ameli_api import AmeliAPI


class FauxReponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self._status = status

    def raise_for_status(self):
        if self._status >= 400:
            raise requests.HTTPError(f"HTTP {self._status}")

    def json(self):
        return self._payload


def _faux_session(payload, journal=None):
    """Retourne une fonction get(...) qui renvoie toujours `payload` et journalise les appels."""
    def get(url, params=None, timeout=None):
        if journal is not None:
            journal.append({"url": url, "params": params})
        return FauxReponse({"results": payload})
    return get


def test_get_effectifs_construit_la_requete():
    api = AmeliAPI()
    journal = []
    api._session.get = _faux_session([{"annee": "2023", "effectif": 322, "densite": 47.1}], journal)

    res = api.get_effectifs("Cardiologues", "75", 2023)

    assert res == [{"annee": "2023", "effectif": 322, "densite": 47.1}]
    appel = journal[0]
    assert appel["url"].endswith("/demographie-effectifs-et-les-densites/records")
    where = appel["params"]["where"]
    assert 'profession_sante="Cardiologues"' in where
    assert 'departement="75"' in where
    assert "year(annee)=2023" in where


def test_get_honoraires_dataset_et_filtre_type():
    api = AmeliAPI()
    journal = []
    api._session.get = _faux_session([], journal)

    api.get_honoraires("Cardiologues", "75", 2023, "Actes")

    appel = journal[0]
    assert "honoraires-detailles" in appel["url"]
    where = appel["params"]["where"]
    assert 'type_honoraires_niveau_1="Actes"' in where


def test_get_honoraires_sans_type_pas_de_filtre():
    api = AmeliAPI()
    journal = []
    api._session.get = _faux_session([], journal)

    api.get_honoraires("Cardiologues", "75", 2023)

    where = journal[0]["params"]["where"]
    assert "type_honoraires_niveau_1" not in where


def test_get_effectifs_par_departement_pagine_et_agrege():
    api = AmeliAPI()
    # 1re page pleine (100 lignes) -> il doit demander une 2e page
    page1 = [{"departement": str(i), "effectif": i, "densite": float(i)} for i in range(100)]
    page2 = [{"departement": "X", "effectif": 5, "densite": 5.0}]

    def get(url, params=None, timeout=None):
        return FauxReponse({"results": page1 if params["offset"] == 0 else page2})

    api._session.get = get

    res = api.get_effectifs_par_departement("Cardiologues", 2023)

    assert len(res) == 101
    assert res["X"] == {"effectif": 5, "densite": 5.0}
    assert res["0"] == {"effectif": 0, "densite": 0.0}


def test_cache_evite_un_second_appel():
    api = AmeliAPI()
    compteur = {"n": 0}

    def get(url, params=None, timeout=None):
        compteur["n"] += 1
        return FauxReponse({"results": [{"a": 1}]})

    api._session.get = get

    r1 = api.get_effectifs("Cardiologues", "75", 2023)
    r2 = api.get_effectifs("Cardiologues", "75", 2023)

    assert r1 == r2 == [{"a": 1}]
    assert compteur["n"] == 1  # le 2e appel est servi par le cache


def test_cache_expire(monkeypatch):
    api = AmeliAPI(cache_duration=0)  # cache immédiatement périmé
    compteur = {"n": 0}

    def get(url, params=None, timeout=None):
        compteur["n"] += 1
        return FauxReponse({"results": [{"a": 1}]})

    api._session.get = get

    api.get_effectifs("Cardiologues", "75", 2023)
    api.get_effectifs("Cardiologues", "75", 2023)

    assert compteur["n"] == 2  # cache périmé -> 2 appels


def test_erreur_reseau_retourne_liste_vide():
    api = AmeliAPI()

    def get(url, params=None, timeout=None):
        raise requests.ConnectionError("réseau indisponible")

    api._session.get = get

    assert api.get_effectifs("Cardiologues", "75", 2023) == []


def test_erreur_http_retourne_liste_vide():
    api = AmeliAPI()
    api._session.get = lambda url, params=None, timeout=None: FauxReponse({}, status=500)

    assert api.get_prescriptions("Cardiologues", "75", 2023) == []
