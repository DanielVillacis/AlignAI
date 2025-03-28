import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///alignai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour