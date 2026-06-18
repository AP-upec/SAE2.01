import os
from pathlib import Path
from dotenv import load_dotenv
# Charge le .env situé à cote de ce fichier, quel que soit le dossier de lancement.
# Sous WSGI (Alwaysdata) le dossier courant n'est pas celui de l'app : sans chemin
# explicite les variables DB ne sont pas lues -> erreur 500 en production.
load_dotenv(Path(__file__).resolve().parent / ".env")
class Config:
    """Configuration de l'application."""
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    # Identifiants administrateur (login simple) — définis dans le .env
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    @classmethod
    def db_url(cls):
        """Construit l'URL de connexion MySQL."""
        return (f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
    f"@{cls.DB_HOST}/{cls.DB_NAME}")