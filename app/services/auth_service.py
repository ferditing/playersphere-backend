from flask import request, current_app
from app.models.coach import Coach
import jwt

def get_current_coach():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Exception("No auth token")
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        coach = Coach.query.get(payload['coach_id'])
        if not coach:
            raise Exception("Coach not found")
        return coach
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")