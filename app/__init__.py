import os

from flasgger import Swagger
from flask import Flask
from sqlalchemy import text

from config import Config

from .extensions import db, login_manager, migrate
from .presentation import role_label, status_label, vehicle_type_icon, vehicle_type_label
from .services import seed_demo_data


def _create_stored_procedures(app: Flask) -> None:
    """Legt die PostgreSQL Stored Procedures an (nur bei PostgreSQL-Verbindung)."""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not uri.startswith('postgresql'):
        return
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'stored_procedures.sql')
    sql_path = os.path.normpath(sql_path)
    if not os.path.exists(sql_path):
        return
    with open(sql_path, encoding='utf-8') as f:
        sql = f.read()
    with db.engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    swagger_config = {
        'headers': [],
        'specs': [
            {
                'endpoint': 'apispec',
                'route': '/api/apispec.json',
                'rule_filter': lambda rule: str(rule).startswith('/api/'),
                'model_filter': lambda tag: True,
            }
        ],
        'static_url_path': '/flasgger_static',
        'swagger_ui': True,
        'specs_route': '/api/docs/',
        'top_text': (
            '<a href="/" style="'
            'display:inline-flex;align-items:center;gap:6px;'
            'padding:8px 16px;margin:12px 0 0 12px;'
            'background:#22c55e;color:#fff;border-radius:6px;'
            'text-decoration:none;font-family:Inter,sans-serif;font-size:14px;font-weight:600;'
            '">'
            '&#8592; Zurück zur Startseite'
            '</a>'
        ),
    }
    swagger_template = {
        'info': {
            'title': 'E-Mobility Bern API',
            'description': 'REST API für das E-Fahrzeug-Verleihsystem Bern',
            'version': '1.0.0',
            'contact': {'name': 'E-Mobility Bern'},
        },
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT-ähnliches API-Token. Format: **Bearer &lt;token&gt;**',
            }
        },
        'basePath': '/',
        'consumes': ['application/json'],
        'produces': ['application/json'],
    }
    Swagger(app, config=swagger_config, template=swagger_template)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .profile.routes import profile_bp
    from .providers.routes import providers_bp
    from .rentals.routes import rentals_bp
    from .api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(providers_bp, url_prefix='/providers')
    app.register_blueprint(rentals_bp, url_prefix='/rentals')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.context_processor
    def inject_template_helpers():
        return {
            'status_label': status_label,
            'role_label': role_label,
            'vehicle_type_label': vehicle_type_label,
            'vehicle_type_icon': vehicle_type_icon,
        }

    with app.app_context():
        db.create_all()
        _create_stored_procedures(app)
        seed_demo_data()

    return app
