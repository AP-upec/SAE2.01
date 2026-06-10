import requests
class AmeliAPI:
    """Service d'accès à l'API data.ameli.fr."""
    BASE_URL = "https://data.ameli.fr/api/explore/v2.1/catalog/datasets"
    def __init__(self, timeout=10):
        self._timeout = timeout
        self._session = requests.Session()
    def get_effectifs(self, profession, departement_code, annee):
        """Effectifs pour une profession, un département et une année.Retourne une liste de dictionnaires {annee, effectif, densite}."""
        where = (
        f"profession_sante=\"{profession}\" AND "
        f"departement=\"{departement_code}\" AND "
        f"year(annee)={annee} AND "
        f"libelle_classe_age=\"Tout âge\" AND "
        f"libelle_sexe=\"tout sexe\""
        )
        return self._requete(
        "demographie-effectifs-et-les-densites",
        {"select": "annee,effectif,densite", "where": where, "limit": 100},
        )

    def get_evolution_effectifs(self, profession, departement_code):
        """Effectifs sur toutes les années disponibles (pour un graphique)."""
        where = (f"profession_sante=\"{profession}\" AND "
        f"departement=\"{departement_code}\" AND "
        f"libelle_classe_age=\"Tout âge\" AND "
        f"libelle_sexe=\"tout sexe\""
        )
        return self._requete(
        "demographie-effectifs-et-les-densites",
        {"select": "annee,effectif,densite", "where": where,
        "order_by": "annee", "limit": 100},
        )
    
    def get_prescriptions(self, profession, departement_code, annee):
        """Postes de prescription (montants) pour une profession, un département et une année."""
        where = (
        f"profession_sante=\"{profession}\" AND "
        f"departement=\"{departement_code}\" AND "
        f"year(annee)={annee} AND "
        f"libelle_poste_prescription!=\"total postes de prescriptions\""
        )
        return self._requete(
        "prescriptions",
        {"select": "libelle_poste_prescription,montant_total_prescription,montant_moyen_prescription",
        "where": where, "limit": 100},
        )

    def get_evolution_prescriptions(self, profession, departement_code):
        """Montant total de prescriptions par année (ligne agrégée)."""
        where = (
        f"profession_sante=\"{profession}\" AND "
        f"departement=\"{departement_code}\" AND "
        f"libelle_poste_prescription=\"total postes de prescriptions\""
        )
        return self._requete(
        "prescriptions",
        {"select": "annee,montant_total_prescription", "where": where,
        "order_by": "annee", "limit": 100},
        )
    
    def get_honoraires(self,type,profession,departement_code): 
        """Honoraires."""
        where = (f"profession_sante=\"{profession}\" AND "
        f"departement=\"{departement_code}\" AND "
        f"type_honoraires_niveau_1=\"{type}\""

        )
        return self._requete(
        "Professionnels de santé libéraux : montants des honoraires par catégorie et par territoire (département, région)",
        {"select": "annee,departement,type_honoraires_niveau_1,type_honoraires_niveau_2,type_honoraires_niveau_3", "where": where,
        "order_by": "annee", "limit": 100},
        )


    def _requete(self, dataset, params):
        """Méthode privée : effectue une requête GET et gère les erreurs."""
        url = f"{self.BASE_URL}/{dataset}/records"
        try:
            resp = self._session.get(url, params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except requests.RequestException as e:
            print(f"[AmeliAPI] Erreur : {e}")
            return []
