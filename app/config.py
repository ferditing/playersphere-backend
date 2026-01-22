import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-default-secret")

class ProductionConfig(Config):
    # Get the URL and fix the postgres prefix if necessary
    raw_uri = os.environ.get("DATABASE_URL")
    if raw_uri and raw_uri.startswith("postgres://"):
        raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = raw_uri

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")