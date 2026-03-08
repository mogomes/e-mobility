import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg://escooter:strongpassword@localhost:5432/escooterdb',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:8000')
