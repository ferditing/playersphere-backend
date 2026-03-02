# 🔐 Admin Setup & Authentication Guide

## Initial Super Admin Creation

The system requires a **Super Admin user** to bootstrap the admin hierarchy. This super admin can then create county admins and national admins.

---

## 📝 Seeding the Super Admin

### **Option 1: Automatic (Recommended)**

When you run the migration and seeding in production:

```bash
# Build command (Render):
pip install -r requirements.txt && python -m flask db upgrade && python seed_db.py
```

This automatically creates:
- ✅ Location data (Kenya counties, constituencies, wards)
- ✅ Initial super admin

**Default Super Admin Credentials:**
```
Email: admin@playersphere.com
Password: AdminPassword123!
Role: super_admin
```

### **Option 2: Manual - Flask CLI**

```bash
flask seed-admin

# You will be prompted:
# Admin email: admin@playersphere.com
# Admin password: ••••••••••••••••••
# Admin full name: System Administrator
```

### **Option 3: Manual - Python Script**

```bash
python seed_db.py
```

---

## 🔑 Changing Default Credentials

**CRITICAL:** Change the default password immediately in production!

```bash
# Using Flask CLI with custom values:
flask seed-admin --email your-email@playersphere.com --password YourSecurePassword123! --name "Your Name"
```

Or modify in [seed_db.py](seed_db.py#L30-L35):

```python
admin = Admin(
    full_name='System Administrator',
    email='admin@playersphere.com',
    password_hash=generate_password_hash('YOUR_NEW_PASSWORD'),  # Change this
    role='super_admin'
)
```

---

## 📊 Admin Role Hierarchy

### **Super Admin** (`super_admin`)
- Full system access across all counties and regions
- Can create/manage county admins and national admins
- Access all competitions and tournaments
- System configuration and settings
- View all reports and analytics

### **National Admin** (`national_admin`)
- Manage national-level tournaments
- Create advancement rules between tiers
- View all national competitions
- Manage other national admins
- Cannot access county-specific data

### **County Admin** (`county_admin`)
- Manage county-level competitions only
- Add teams from their county only
- Generate fixtures for county tournaments
- Cannot create other admins
- Cannot access other counties' data

---

## 👥 Creating Additional Admin Users

### Method 1: Via Backend CLI

```bash
# Create a county admin
flask seed-admin --email county-admin@playersphere.com --password SecurePass123! --name "County Admin Name"
```

### Method 2: Via Admin Dashboard (Frontend)

Once you're logged in as super admin:
1. Go to `/admin` (Admin Dashboard)
2. Click "Admin Users > Create New Admin"
3. Fill in email, password, name
4. Select role: `county_admin` or `national_admin`
5. Assign county (only for county admins)
6. Click Create

---

## 🔐 Authentication Flow

### Login as Admin

**Frontend:**
```
URL: /login
Email: admin@playersphere.com
Password: AdminPassword123!
```

**The system will:**
1. Authenticate credentials against hashed password
2. Return JWT token with admin role
3. Grant access to admin routes (`/admin`, `/admin/competitions`)
4. Show admin menu in dashboard header

### Admin Routes (Protected)

All admin routes require:
- Valid JWT token
- User role in `['super_admin', 'county_admin', 'national_admin']`

```typescript
// Example: Check if user is admin
if (user?.role && ['super_admin', 'county_admin', 'national_admin'].includes(user.role)) {
  // Show admin menu
}
```

---

## 🚀 Production Deployment

### **Step 1: Database Setup**
On Render, your `buildCommand` should be:
```bash
pip install -r requirements.txt && python -m flask db upgrade && python seed_db.py
```

### **Step 2: Access Admin Dashboard**

After deployment:
1. Navigate to `https://playersphere-backend.onrender.com/admin`
2. Login with default credentials
3. **CHANGE PASSWORD IMMEDIATELY**

### **Step 3: Create County/National Admins**

Via Admin Dashboard → Admin Users:
- Create county admins for each county
- Create national admins for tournament oversight

---

## ⚠️ Security Considerations

### Password Requirements
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers, special characters
- Change default password in production
- No common/dictionary words

### Token Security
- JWT tokens stored in `localStorage` (frontend)
- Tokens expire after session timeout
- HTTPS required in production
- SameSite cookie policy enabled

### Database Security
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Used bcrypt for hash algorithm
- Never store plain-text passwords
-County_id foreign key prevents cross-county access (at database level)

---

## 🆘 Troubleshooting

### "Admin already exists"
```
[!] Admin with email 'admin@playersphere.com' already exists. Skipping...
```
**Solution:** Use a different email or delete the existing admin from the database:
```bash
# In Flask shell:
from app.models import Admin
admin = Admin.query.filter_by(email='admin@playersphere.com').delete()
db.session.commit()
```

### "Cannot create multiple super admins"
The system enforces one super admin. To change ownership:
1. Create new super admin with different email
2. Remove old super admin from database
3. Re-run seeding

### "Admin login fails"
Check:
1. Admin exists: `Admin.query.all()` in Flask shell
2. Password hash: `admin.password_hash` is not None
3. Email is exact match (case-sensitive)
4. Role is valid: `super_admin`, `county_admin`, or `national_admin`

---

## 📝 Admin Account Audit

To list all admin accounts:

```bash
# In Flask shell:
from app.models import Admin

# Get all admins
admins = Admin.query.all()
for admin in admins:
    print(f"{admin.full_name} ({admin.email}) - Role: {admin.role}")
```

---

## 🔄 Resetting Admin Password

If you lose access:

### Production (Render):
1. Start a one-off job
2. Run: `flask shell`
3. Execute:
```python
from app.models import Admin
from werkzeug.security import generate_password_hash
admin = Admin.query.filter_by(email='admin@playersphere.com').first()
admin.password_hash = generate_password_hash('NewPassword123!')
db.session.commit()
```

### Local Development:
Same as above in your local Flask shell

---

## 📚 Related Files

- [Admin Model](../app/models/admin.py) - Admin table schema
- [Seed Admin Script](../app/services/seed_admin.py) - CLI command
- [Seed DB Script](../seed_db.py) - Standalone seeding
- [Admin Dashboard](../../playersphere-frontend/src/pages/AdminDashboard.tsx) - Frontend

---

**Status:** ✅ Ready for production deployment
