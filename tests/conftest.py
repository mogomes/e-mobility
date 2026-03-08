import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app():
    app = create_app(
        {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret',
        }
    )
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def rider_credentials(app):
    with app.app_context():
        rider = User.query.filter_by(username='rider1').first()
        return {'username': rider.username, 'password': 'Rider123!'}


@pytest.fixture()
def provider_credentials(app):
    with app.app_context():
        provider = User.query.filter_by(username='provider1').first()
        return {'username': provider.username, 'password': 'Provider123!'}
