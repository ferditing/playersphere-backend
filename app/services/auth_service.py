from flask import request, current_app
from app.models.coach import Coach
from app.models.admin import Admin
import jwt

def get_current_coach():
    """Get current coach from token - for coach endpoints only"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Exception("No auth token")
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # If this is an admin token, raise an error
        if 'admin_id' in payload:
            raise Exception("Admin tokens cannot access coach endpoints")
        
        coach = Coach.query.get(payload['coach_id'])
        if not coach:
            raise Exception("Coach not found")
        return coach
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def get_current_coach_or_none():
    """Get current coach from token, returns None if admin token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # If this is an admin token, return None
        if 'admin_id' in payload:
            return None
        
        coach = Coach.query.get(payload['coach_id'])
        return coach
    except:
        return None

def get_current_user():
    """Get current user (coach or admin) from token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise Exception("No auth token")
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        # Check if it's an admin token
        if 'admin_id' in payload:
            admin = Admin.query.get(payload['admin_id'])
            if not admin:
                raise Exception("Admin not found")
            return admin
        
        # Otherwise it's a coach token
        coach = Coach.query.get(payload['coach_id'])
        if not coach:
            raise Exception("Coach not found")
        return coach
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")