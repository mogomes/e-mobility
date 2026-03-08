from flask import Flask

from config import Config

from .extensions import db, login_manager, migrate
from .presentation import role_label, status_label, vehicle_type_emoji, vehicle_type_label
from .services import seed_demo_data


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .providers.routes import providers_bp
    from .rentals.routes import rentals_bp
    from .api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(providers_bp, url_prefix='/providers')
    app.register_blueprint(rentals_bp, url_prefix='/rentals')
    app.register_blueprint(api_bp, url_prefix='/api')


    @app.context_processor
    def inject_template_helpers():
        return {
            'status_label': status_label,
            'role_label': role_label,
            'vehicle_type_label': vehicle_type_label,
            'vehicle_type_emoji': vehicle_type_emoji,
        }

    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app
