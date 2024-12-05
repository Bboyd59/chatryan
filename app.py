import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
from flask_login import AnonymousUserMixin

class Anonymous(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_DURATION'] = 1800
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production
    app.config['LOGIN_DISABLED'] = True  # Disable login requirement for non-admin routes
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.admin_login'

    with app.app_context():
        from models import User
        db.create_all()

        # Register blueprints
        from auth import auth_bp
        from routes import main_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)

    return app
