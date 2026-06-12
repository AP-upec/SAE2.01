from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session
from config import Config
from models.db import Session
from models.dimensions import (Region, Departement, ProfessionSante,
                               TypeHonoraire, TypePrescription)

bp_auth = Blueprint("auth", __name__, url_prefix="/admin")


def login_required(vue):
    """Protège une route : redirige vers le login si l'admin n'est pas connecté."""
    @wraps(vue)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("auth.login"))
        return vue(*args, **kwargs)
    return wrapper


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    """Formulaire de connexion administrateur (identifiants depuis le .env)."""
    erreur = None
    if request.method == "POST":
        identifiant = request.form.get("identifiant", "")
        mot_de_passe = request.form.get("mot_de_passe", "")
        if (Config.ADMIN_PASSWORD
                and identifiant == Config.ADMIN_USER
                and mot_de_passe == Config.ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("auth.statistiques"))
        erreur = "Identifiant ou mot de passe incorrect."
    return render_template("admin_login.html", erreur=erreur)


@bp_auth.route("/logout")
def logout():
    """Déconnexion : vide la session."""
    session.pop("admin", None)
    return redirect(url_for("auth.login"))


@bp_auth.route("/")
@login_required
def statistiques():
    """Page de statistiques réservée à l'administrateur."""
    session_bd = Session()
    try:
        stats = {
            "regions": session_bd.query(Region).count(),
            "departements": session_bd.query(Departement).count(),
            "professions": session_bd.query(ProfessionSante).count(),
            "types_honoraires": session_bd.query(TypeHonoraire).count(),
            "types_prescriptions": session_bd.query(TypePrescription).count(),
        }
    finally:
        session_bd.close()
    return render_template("admin.html", stats=stats)
