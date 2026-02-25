# Location Models Setup Guide

## Overview

This guide covers the new location hierarchy system: **Country → Region → County → Ward**

The system is designed to support:
- Multiple countries (Kenya, Uganda, Tanzania, Rwanda ready)
- Region-based organization
- County-level coaching and team management
- Ward-level granularity (for future use)

## Models Created

### 1. **Country Model** (`app/models/country.py`)
Represents countries in the system.

```python
from app.models import Country

# Create/retrieve a country
kenya = Country.query.filter_by(code='KE').first()
```

**Fields:**
- `id` (UUID, Primary Key)
- `name` (Text, Unique) - e.g., "Kenya"
- `code` (String[2], Unique) - ISO 3166-1 alpha-2 code (e.g., 'KE')
- `created_at`, `updated_at` (Timestamps)

---

### 2. **Region Model** (`app/models/region.py`)
Groups counties within a country.

```python
from app.models import Region

# Get all regions in Kenya
kenya_regions = Region.query.filter_by(country_id=kenya.id).all()

# Get specific region
central = Region.query.filter_by(name='Central').first()
counties = central.counties  # Access counties via relationship
```

**Fields:**
- `id` (UUID, Primary Key)
- `country_id` (UUID, Foreign Key → Country)
- `name` (Text) - e.g., "Central", "Nyanza"
- `code` (String[20], Optional) - e.g., 'KE_CENTRAL'
- `created_at`, `updated_at` (Timestamps)

**Unique Constraint:** `(country_id, name)` - Region name must be unique per country

---

### 3. **County Model** (`app/models/county.py`)
Represents counties where teams and coaches operate.

```python
from app.models import County

# Get a county
nairobi = County.query.filter_by(name='Nairobi').first()

# Get all counties in a region
central_counties = County.query.filter_by(region_id=central_region.id).all()

# Access wards in county
wards = nairobi.wards

# Access coaches in county
coaches = nairobi.coaches

# Access teams in county
teams = nairobi.teams
```

**Fields:**
- `id` (UUID, Primary Key)
- `region_id` (UUID, Foreign Key → Region)
- `name` (Text) - e.g., "Nairobi", "Kisumu"
- `code` (String[20], Optional) - e.g., 'KE_NAIROBI'
- `created_at`, `updated_at` (Timestamps)

**Unique Constraint:** `(region_id, name)` - County name must be unique per region

**Relationships:**
- `wards` - All wards in this county
- `coaches` - All coaches operating in this county
- `teams` - All teams from this county
- `admins` - All county admins managing this county

---

### 4. **Ward Model** (`app/models/ward.py`)
Sub-divisions within counties (for future player/team localization).

```python
from app.models import Ward

# Get wards in Nairobi
nairobi_wards = Ward.query.filter_by(county_id=nairobi_county.id).all()

# Specific ward
embakasi = Ward.query.filter_by(name='Embakasi Central').first()
```

**Fields:**
- `id` (UUID, Primary Key)
- `county_id` (UUID, Foreign Key → County)
- `name` (Text) - e.g., "Dagoretti North"
- `code` (String[20], Optional)
- `created_at`, `updated_at` (Timestamps)

**Unique Constraint:** `(county_id, name)` - Ward name must be unique per county

---

## Coach & Team Updates

### Coach Table Additions

When coaches are created, they must now be associated with a county:

```python
from app.models import Coach, County

nairobi = County.query.filter_by(name='Nairobi').first()

coach = Coach(
    full_name="John Doe",
    email="john@example.com",
    phone="+254712345678",
    password_hash=hashed_password,
    county_id=nairobi.id,  # NEW: Required for county scoping
    email_verified=False,  # NEW: OTP verification
    must_change_password=False,  # NEW: For admin-created accounts
    created_by_admin_id=None  # NEW: Admin who created this coach (if any)
)
```

**New Columns:**
- `county_id` (UUID, Foreign Key → County, Nullable) - Home county for this coach
- `email_verified` (Boolean, Default: False) - OTP verification status
- `must_change_password` (Boolean, Default: False) - Force password change on first login
- `created_by_admin_id` (UUID, Foreign Key → Admin, Nullable) - Admin who created account

---

### Team Table Additions

Teams are now tied to their home county:

```python
team = Team(
    name="FC Nairobi United",
    coach_id=coach.id,
    county_id=county.id,  # NEW: Home county
    team_type="U17",
    created_by_admin_id=None  # NEW: Admin who created team (if any)
)
```

**New Columns:**
- `county_id` (UUID, Foreign Key → County, Nullable)
- `created_by_admin_id` (UUID, Foreign Key → Admin, Nullable)

---

## Database Migration

### Run Migration

```bash
# Generate migration (if not already done)
flask db migrate -m "Add location hierarchy tables"

# Apply migration
flask db upgrade
```

The migration file `1a2b3c4d5e6f_add_location_hierarchy.py` will:
1. Create `countries`, `regions`, `counties`, `wards` tables
2. Add `county_id`, `email_verified`, `must_change_password`, `created_by_admin_id` to `coaches`
3. Add `county_id`, `created_by_admin_id` to `teams`
4. Create necessary indexes for performance

---

## Seeding Location Data

Kenya location data is pre-configured and can be seeded via Flask CLI:

### Seed Kenya Data

```bash
flask seed-locations
```

This command will:
1. Create **Kenya** country record
2. Create **8 regions** (Central, Coast, Eastern, Nairobi, North Eastern, Nyanza, Rift Valley, Western)
3. Create **47 counties** under their respective regions
4. Create **wards** for select counties (Nairobi, Kiambu, Kisumu, Mombasa, Nakuru)

### Available Commands

```bash
# Seed locations
flask seed-locations

# Clear all locations (WARNING: destructive)
flask clear-locations
```

---

## API Endpoints (to be created)

Example endpoints for location hierarchy:

```
GET    /api/countries
       → { countries: [{ id, name, code }, ...] }

GET    /api/countries/{country_id}/regions
       → { regions: [{ id, name, code }, ...] }

GET    /api/regions/{region_id}/counties
       → { counties: [{ id, name, code }, ...] }

GET    /api/counties/{county_id}/wards
       → { wards: [{ id, name, code }, ...] }

GET    /api/counties/{county_id}/coaches
       → { coaches: [...] }

GET    /api/counties/{county_id}/teams
       → { teams: [...] }
```

---

## Service Functions

The `location_service.py` provides utility functions:

```python
from app.services.location_service import (
    seed_locations,
    clear_locations,
    get_county_by_name,
    get_region_by_name,
    get_all_regions,
    get_counties_by_region,
    get_wards_by_county
)

# Examples
nairobi_county = get_county_by_name('Nairobi')
central_region = get_region_by_name('Central')
all_regions = get_all_regions()
central_counties = get_counties_by_region(central_region.id)
nairobi_wards = get_wards_by_county(nairobi_county.id)
```

---

## Adding Ward Data

Currently, wards are seeded for these counties:
- Nairobi
- Kiambu
- Kisumu
- Mombasa
- Nakuru

To add ward data for other counties, update `app/services/location_seed_data.py`:

```python
KENYA_WARDS = {
    'Nairobi': [...],  # Existing
    'YourCounty': [
        'Ward 1',
        'Ward 2',
        'Ward 3',
    ]
}
```

Then re-run:
```bash
flask clear-locations
flask seed-locations
```

---

## Permission Model (Preview)

When Admin/National Admin features are implemented:

```python
# Permission check for county admin
def can_manage_county(admin, county_id):
    if admin.role == 'super_admin':
        return True  # Can manage all
    if admin.role == 'county_admin':
        return admin.county_id == county_id  # Can only manage their county
    return False
```

---

## Summary

| Table | Purpose | Key FK |
|-------|---------|--------|
| Country | Global regions | - |
| Region | Groups counties | Country |
| County | Coaching/team unit | Region |
| Ward | Sub-county areas | County |
| Coach | Coach + location | County |
| Team | Team + location | County |

**Next Steps:**
1. ✅ Models created
2. ✅ Migration created
3. ✅ Seeding service created
4. ⏳ Run migration: `flask db upgrade`
5. ⏳ Seed data: `flask seed-locations`
6. ⏳ Create location API endpoints
7. ⏳ Implement Admin model with role-based access
8. ⏳ Update signup flow with county selection + OTP
