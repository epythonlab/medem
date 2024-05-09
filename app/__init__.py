from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from sqlalchemy.exc import OperationalError, InvalidRequestError, NoForeignKeysError
import logging
from werkzeug.security import generate_password_hash
from flask_login import LoginManager


# Initialize SQLAlchemy
db = SQLAlchemy()
# Initialize LoginManager
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Application configuration
    app.config.from_object("settings.Config")

    # Initialize Plugins
    db.init_app(app)

    # Set up logging configuration
    logging.basicConfig(level=logging.ERROR, filename='error.log',
                        filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

    # init login_manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message = "Please enter valid email and password!"
    login_manager.login_message_category = "info"

    # Import blueprints
    from app.routes import index_bp
    from app.routes import auth_bp
    from app.routes import user_bp
    # Register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    

    # Create database tables within application context
    with app.app_context():
        from app.models.users import Role, User
        try:
            # Create database tables
            db.create_all()

            # Create roles if they don't exist
            user_datastore = SQLAlchemyUserDatastore(db, User, Role)
            security = Security(app, user_datastore)
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='Administrator')
                db.session.add(admin_role)

            # Create a default admin user if no users exist
            if not User.query.filter(User.roles.contains(admin_role)).first():
                default_admin = User(
                    email='admin@admin.com', password=generate_password_hash('admin'), active=True)
                default_admin.roles.append(admin_role)
                import uuid
                default_admin.fs_uniquifier = uuid.uuid4()
                db.session.add(default_admin)

            db.session.commit()

        except (InvalidRequestError, NoForeignKeysError):
            # Handle database creation error
            app.logger.error("Failed to create database tables")
            raise
        except OperationalError as e:
            # Handle connection error
            error_msg = "Error connecting to MySQL server: %s" % str(e)
            print(error_msg)
            print("Make sure your MySQL server is running and the connection details are correct.")
            raise
    return app
