from flask import Flask
from .extensions import ma, limiter, cache
from .models import db
from .blueprints.customers import customers_db
from .blueprints.mechanics import mechanics_db
from .blueprints.service_tickets import tickets_db
from .blueprints.inventory import inventory_db
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API URL (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Your API's Name"
    }
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

# Load app configuration
    app.config.from_object(f'config.{config_name}')


    #initialize extensions 
    ma.init_app(app) 
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)




    #register blueprint
    app.register_blueprint(customers_db, url_prefix='/customers')
    app.register_blueprint(mechanics_db, url_prefix='/mechanics')
    app.register_blueprint(tickets_db, url_prefix='/service_tickets')
    app.register_blueprint(inventory_db, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL) #Registering our swagger blueprint
  
   




    return app

