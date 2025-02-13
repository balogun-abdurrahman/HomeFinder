from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from home import config
from home.models import db


csrf =CSRFProtect()

def create_app():     
    from home import models
    app = Flask(__name__,instance_relative_config=True)

    app.config.from_pyfile("config.py")
    app.config.from_object(config.BaseConfig)

    # db = SQLAlchemy()
    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)

    return app

app = create_app()
from home import user_routes,admin_routes
# from home import models