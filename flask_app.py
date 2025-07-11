import os
from app import create_app
from app.models import db

#app = create_app("DevelopmentConfig")
app = create_app('ProductionConfig')

with app.app_context():
    #db.drop_all()
    db.create_all()

# Fix for Render deployment: bind to 0.0.0.0 and use PORT environment variable
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)







