

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Password1@localhost/garage_db'
    DEBUG = True

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True

class ProductionConfig:
    # Add logging to diagnose the issue
    print(f"DEBUG: Loading ProductionConfig")
    print(f"DEBUG: SQLALCHEMY_DATABASE_URI from env: {os.getenv('SQLALCHEMY_DATABASE_URI')}")
    print(f"DEBUG: All env vars starting with SQL: {[k for k in os.environ.keys() if k.startswith('SQL')]}")
    
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    # Validate the URI is set
    if not SQLALCHEMY_DATABASE_URI:
        print("ERROR: SQLALCHEMY_DATABASE_URI is not set in environment variables!")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            if 'SQL' in key.upper() or 'DATABASE' in key.upper():
                print(f"  {key}: {os.environ[key]}")
    else:
        print(f"SUCCESS: SQLALCHEMY_DATABASE_URI is set to: {SQLALCHEMY_DATABASE_URI[:50]}...")