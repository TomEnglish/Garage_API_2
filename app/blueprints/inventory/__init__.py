from flask import Blueprint

inventory_db = Blueprint("inventory_db", __name__)

from . import routes