import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ["SECRET_KEY"]

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
