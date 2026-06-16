"""Point d'entrée WSGI pour le serveur Alwaysdata."""
from app import app as application
# Alwaysdata s'attend à une variable nommée "application"