from flask import Blueprint

customers_db = Blueprint("customers_db", __name__)

from . import routes