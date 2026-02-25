from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.coach import Coach
from app.extensions.db  import db
from app.services.otp_service import send_signup_otp, verify_signup_otp, is_email_verified_for_signup
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

    email = data['email'].lower().strip()
    if not is_email_verified_for_signup(email):
        return jsonify({"error": "Email not verified, Please verify OTP first"}), 400

    if Coach.query.filter_by(phone=data['phone']).first():
        return jsonify({"error": "Phone already exists"}), 400
    if Coach.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    coach = Coach(
        full_name=data['full_name'],
        email=email,
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


@bp.post("/send-otp")
def send_otp():
    data = request.json or {}
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is requres"}), 400
    
    if Coach.query.filter_by(email=email.lower().strip()).first():
        return jsonify({"error": "Email already exists"}), 400
    
    try:
        send_signup_otp(email)
        return jsonify({"message": "OTP sent to email"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@bp.post("/verify-otp")
def verify_otp():
    data = request.json or {}
    email = data.get("email")
    otp_code = data.get("otp")


    if not email or not otp_code:
        return jsonify({"error": "Email and OTP are required"}), 400    
    
    try:
        verify_signup_otp(email, otp_code)
        return jsonify({"message": "Email verified succesfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400