from flask import Blueprint

mechanics_db = Blueprint("mechanics_db", __name__)

from . import routes