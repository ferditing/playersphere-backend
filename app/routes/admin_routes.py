from flask import Blueprint, request, jsonify
from app.extensions.db import db
from app.services.auth_service import get_current_user
from app.models.admin import Admin
from app.models.county import County
from werkzeug.security import generate_password_hash

bp = Blueprint("admins", __name__, url_prefix="/api/admins")

@bp.post("/", strict_slashes=False)
def create_admin():
    """Admin endpoint to create a new admin"""
    try:
        user = get_current_user()
        
        # Verify admin access (only super_admin and national_admin can create admins)
        if not isinstance(user, Admin) or user.role not in ['super_admin', 'national_admin']:
            return jsonify({"error": "Only national admins can create admins"}), 403
        
        data = request.get_json() or {}
        
        # Validate required fields
        if not data.get("full_name"):
            return jsonify({"error": "Full name is required"}), 400
        if not data.get("email"):
            return jsonify({"error": "Email is required"}), 400
        if not data.get("password"):
            return jsonify({"error": "Password is required"}), 400
        if not data.get("role"):
            return jsonify({"error": "Role is required"}), 400
        
        # Validate role
        valid_roles = ['county_admin', 'national_admin']
        if data.get("role") not in valid_roles:
            return jsonify({"error": "Role must be 'county_admin' or 'national_admin'"}), 400
        
        # If county_admin, county_id or county_name is required
        county_id = None
        if data.get("role") == "county_admin":
            if not data.get("county_id"):
                return jsonify({"error": "County is required for county admins"}), 400
            
            # Try to look up county by name (from frontend)
            county_name = data.get("county_id")
            county = County.query.filter_by(name=county_name).first()
            if not county:
                return jsonify({"error": f"County '{county_name}' not found"}), 404
            county_id = county.id
        
        # Check if email already exists
        if Admin.query.filter_by(email=data.get("email")).first():
            return jsonify({"error": "Email already exists"}), 400
        
        # Create new admin
        admin = Admin(
            full_name=data.get("full_name"),
            email=data.get("email"),
            password_hash=generate_password_hash(data.get("password")),
            role=data.get("role"),
            county_id=county_id
        )
        
        db.session.add(admin)
        db.session.commit()
        
        return jsonify(admin.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.get("/", strict_slashes=False)
def list_admins():
    """List all admins. Only admins can do this."""
    try:
        user = get_current_user()
        
        if not isinstance(user, Admin):
            return jsonify({"error": "Only admins can list admins"}), 403
        
        # County admins can only list admins in their county
        if user.role == 'county_admin':
            admins = Admin.query.filter(
                (Admin.county_id == user.county_id) | 
                (Admin.role == 'national_admin')
            ).all()
        else:
            # National/super admins can see all admins
            admins = Admin.query.all()
        
        return jsonify([admin.to_dict() for admin in admins]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@bp.get("/<admin_id>", strict_slashes=False)
def get_admin(admin_id):
    """Get a specific admin"""
    try:
        user = get_current_user()
        
        if not isinstance(user, Admin):
            return jsonify({"error": "Only admins can view admin details"}), 403
        
        admin = Admin.query.filter_by(id=admin_id).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        # County admins can only view admins in their county or national admins
        if user.role == 'county_admin':
            if admin.county_id != user.county_id and admin.role != 'national_admin':
                return jsonify({"error": "Unauthorized"}), 403
        
        return jsonify(admin.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@bp.put("/<admin_id>", strict_slashes=False)
def update_admin(admin_id):
    """Update an admin. Only super/national admins can do this."""
    try:
        user = get_current_user()
        
        if not isinstance(user, Admin) or user.role not in ['super_admin', 'national_admin']:
            return jsonify({"error": "Only national admins can update admins"}), 403
        
        admin = Admin.query.filter_by(id=admin_id).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        data = request.get_json() or {}
        
        # Update fields
        if "full_name" in data:
            admin.full_name = data["full_name"]
        if "email" in data:
            # Check if email is already taken by another admin
            existing = Admin.query.filter_by(email=data["email"]).first()
            if existing and existing.id != admin.id:
                return jsonify({"error": "Email already exists"}), 400
            admin.email = data["email"]
        if "role" in data:
            if data["role"] not in ['county_admin', 'national_admin']:
                return jsonify({"error": "Invalid role"}), 400
            admin.role = data["role"]
        if "county_id" in data:
            admin.county_id = data["county_id"]
        
        db.session.commit()
        return jsonify(admin.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.delete("/<admin_id>", strict_slashes=False)
def delete_admin(admin_id):
    """Delete an admin. Only super/national admins can do this."""
    try:
        user = get_current_user()
        
        if not isinstance(user, Admin) or user.role not in ['super_admin', 'national_admin']:
            return jsonify({"error": "Only national admins can delete admins"}), 403
        
        admin = Admin.query.filter_by(id=admin_id).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        # Prevent deleting yourself
        if admin.id == user.id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        db.session.delete(admin)
        db.session.commit()
        
        return jsonify({"message": "Admin deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
