import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
import sys

# Configure logging to show detailed error messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    from models import User
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
    app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get("WTF_CSRF_SECRET_KEY") or app.secret_key
    
    # Set up database URL
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set")
        raise ValueError("DATABASE_URL environment variable is required")
        
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    logger.info(f"Configuring database connection...")
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
    )
    
    try:
        db.init_app(app)
        logger.info("Database initialization successful")
        
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        logger.info("Login manager initialized")

        with app.app_context():
            # Import models and create tables
            from models import User, Chat, Message, KnowledgeBase
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")

            # Register blueprints
            from auth import auth_bp
            from routes import main_bp
            app.register_blueprint(auth_bp)
            app.register_blueprint(main_bp)
            logger.info("Blueprints registered successfully")
            
    except Exception as e:
        logger.error(f"Error during app initialization: {str(e)}", exc_info=True)
        raise

    return app
