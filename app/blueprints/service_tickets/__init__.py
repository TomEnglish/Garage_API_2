from flask import Blueprint

tickets_db = Blueprint('tickets_db', __name__)

# The following line should be included if there's a routes.py file
# in the app/blueprints/service_tickets/ directory.
# Please check for the existence of app/blueprints/service_tickets/routes.py
# and uncomment the line below if it exists.
from . import routes