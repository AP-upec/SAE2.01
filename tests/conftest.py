"""Fixtures partagées pour les tests.

Les tests d'intégration utilisent une base SQLite en mémoire (pas la base MySQL
de prod) : on reconfigure le sessionmaker `models.db.Session` pour qu'il pointe
dessus, puis on crée et on remplit les tables avec quelques données de test.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import models.db as db
from models.dimensions import (
    Base, Region, Departement, ProfessionSante, TypeHonoraire, TypePrescription,
)


def _remplir(session):
    """Insère un petit jeu de données représentatif."""
    idf = Region(code="11", libelle="Île-de-France")
    ara = Region(code="84", libelle="Auvergne-Rhône-Alpes")
    session.add_all([idf, ara])
    session.flush()  # pour obtenir les id

    session.add_all([
        Departement(code="75", libelle="Paris", region_id=idf.id),
        Departement(code="77", libelle="Seine-et-Marne", region_id=idf.id),
        Departement(code="69", libelle="Rhône", region_id=ara.id),
    ])

    session.add_all([
        ProfessionSante(libelle="Ensemble des médecins"),
        ProfessionSante(libelle="Cardiologues"),
        ProfessionSante(libelle="Ensemble des chirurgiens-dentistes"),
    ])

    # Plusieurs lignes partagent le même niveau_1 ("Actes") : sert à vérifier
    # que le menu des types d'honoraires est bien dédupliqué.
    session.add_all([
        TypeHonoraire(niveau_1="Actes", niveau_2="Actes cliniques", niveau_3="Consultations"),
        TypeHonoraire(niveau_1="Actes", niveau_2="Actes techniques", niveau_3=None),
        TypeHonoraire(niveau_1="Rémunérations forfaitaires", niveau_2="ROSP", niveau_3=None),
        TypeHonoraire(niveau_1="Dépassements", niveau_2=None, niveau_3=None),
    ])

    session.add_all([
        TypePrescription(libelle="Médicaments"),
        TypePrescription(libelle="Dispositifs médicaux"),
    ])
    session.commit()


@pytest.fixture
def db_sqlite():
    """Base SQLite en mémoire branchée sur le sessionmaker de l'application."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # une seule connexion -> la base en mémoire persiste
    )
    Base.metadata.create_all(engine)
    db.Session.configure(bind=engine)  # les contrôleurs utilisent ce sessionmaker

    session = db.Session()
    try:
        _remplir(session)
    finally:
        session.close()

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def client(db_sqlite):
    """Client de test Flask, avec la base SQLite déjà peuplée."""
    from app import app
    app.config.update(TESTING=True, SECRET_KEY="test")
    with app.test_client() as c:
        yield c
