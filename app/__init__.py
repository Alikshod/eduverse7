from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'rahasia123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eduverse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    from app import models
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main
    app.register_blueprint(main)
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
