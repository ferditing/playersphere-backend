from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.coach import Coach
from app.extensions.db  import db
import jwt
import datetime

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.post("/login")
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    coach = Coach.query.filter_by(email=email).first()
    if not coach or not coach.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        'coach_id': str(coach.id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token, "user": coach.to_dict()})

@bp.post("/signup")
def signup():
    data = request.json
    if not data.get('email'):
        return jsonify({"error": "Email is required"}), 400
    if Coach.query.filter_by(phone=data['phone']).first():
        return jsonify({"error": "Phone already exists"}), 400
    if Coach.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    coach = Coach(
        full_name=data['full_name'],
        email=data['email'],
        phone=data['phone'],
        whatsapp_number=data.get('whatsapp_number'),
        country=data['country'],
        region=data.get('region'),
        city=data.get('city')
    )
    coach.set_password(data['password'])
    db.session.add(coach)
    db.session.commit()

    token = jwt.encode({
        'coach_id': str(coach.id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({"token": token, "user": coach.to_dict()})

@bp.get("/me")
def me():
    from app.services.auth_service import get_current_coach
    coach = get_current_coach()
    return jsonify(coach.to_dict())