from flask import Flask
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS
from app.extensions.db import db
from app.extensions.migrate import migrate
from app import models
import os

def create_app():
    app = Flask(__name__)

    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path, override=True)

    # 2. FIX: Check if we are on Render, otherwise use Development
    # Render automatically sets an environment variable called 'RENDER'
    if os.environ.get("RENDER"):
        app.config.from_object("app.config.ProductionConfig")
    else:
        app.config.from_object("app.config.DevelopmentConfig")

    # Enable CORS for development with comprehensive settings
    CORS(
        app, 
        origins=[
            "http://localhost:8080", 
            "http://localhost:3000", 
            "http://127.0.0.1:8080", 
            "http://127.0.0.1:3000", 
            "http://10.50.178.172:8080/",
            "https://playersphere-6ee65.web.app"
        ], 
        supports_credentials=True, 
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"], 
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"], 
        expose_headers=["Content-Type", "Authorization"]
    )

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.teams import bp as teams_bp
    from app.routes.players import bp as players_bp
    from app.routes.public import bp as public_bp
    from app.routes.matches import bp as matches_bp
    from app.routes.messages import bp as messages_bp
    from app.routes.match_interests import bp as match_interests_bp
    from app.routes.coaches import bp as coaches_bp
    from app.routes.match_events import bp as match_events_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(match_interests_bp)
    app.register_blueprint(coaches_bp)
    app.register_blueprint(match_events_bp)

    return app