from flask import Blueprint, render_template, request
from models.db import Session
from models.dimensions import Region, ProfessionSante, Departement
from services.ameli_api import AmeliAPI

bp_page = Blueprint("page", __name__)
api = AmeliAPI()

@bp_page.route("/page")
def afficher():
        return render_template(
            "page.html",
        )