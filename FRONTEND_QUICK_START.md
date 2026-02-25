# 🚀 Frontend Developer - Quick Start Brief

## Executive Summary

**Status:** ✅ Backend API is COMPLETE and PRODUCTION-READY  
**Endpoints:** 16 RESTful endpoints  
**Base URL:** `http://localhost:5000/api/competitions`  
**Documentation:** See `FRONTEND_INTEGRATION_GUIDE.md` in backend repo

---

## What You're Building

A **Tournament Management System** for PlayerSphere that allows admins to:
1. Create competitions (county, regional, national)
2. Add teams (auto or manual)
3. Generate schedules (different formats)
4. Track standings in real-time
5. Advance teams to next tiers (auto or manual)

---

## 🎯 16 API Endpoints (All Ready)

### Competition Management (4)
```
POST   /competitions                     Create
GET    /competitions                     List
GET    /competitions/{id}                Get with standings
PATCH  /competitions/{id}                Update
```

### Team Management (3)
```
POST   /competitions/{id}/teams          Add teams (auto)
POST   /competitions/{id}/teams/manual   Add teams (manual)
GET    /competitions/{id}/teams          List teams
```

### Schedule (2)
```
POST   /competitions/{id}/generate-fixtures  Generate
GET    /competitions/{id}/fixtures            List matches
```

### Standings (1)
```
GET    /competitions/{id}/standings      Get standings
```

### Advancement (5)
```
GET    /competitions/{from}/to/{to}/eligible-teams
POST   /competitions/{from}/advance-to/{to}
POST   /competitions/{from}/advance-manual/{to}
POST   /competitions/{id}/apply-rules
GET    /competitions/{from}/advancement-summary
```

---

## 📦 Key Data Models for Frontend

```typescript
Competition {
  id, season_id, name, stage_level, format_type, legs,
  status, points_win, points_draw, points_loss, max_teams
}

Match {
  id, home_team_id, away_team_id, match_date, venue,
  status, home_score, away_score, competition_id, group_id
}

Standing {
  team_id, team_name, played, wins, draws, losses,
  points, goals_for, goals_against, goal_difference
}
```

---

## 🖼️ UI Components You Need to Build

### Pages
1. **Competition List** - Dashboard showing all tournaments
2. **Competition Detail** - Full tournament view with tabs
3. **Create Competition** - Form to create new tournament
4. **Teams Management** - Add/manage tournament teams
5. **Fixtures View** - Show schedule of matches
6. **Standings Table** - Rankings with all stats
7. **Advancement Control** - Promote teams to next tier

### Core Forms
- Create Competition
- Add Teams (2 variants: auto & manual)
- Generate Fixtures
- Manual Advancement
- Update Competition Config

---

## 📋 Implementation Order (Recommended)

**Week 1:**
1. Setup API client (axios/fetch)
2. Build Competition List page
3. Build Create Competition form

**Week 2:**
4. Build Competition Detail page
5. Build Teams management UI
6. Build Add Teams form (both variants)

**Week 3:**
7. Build Fixtures/Schedule page
8. Build Standings table
9. Implement Generate Fixtures

**Week 4:**
10. Build Advancement UI
11. Implement all advancement endpoints
12. Polish & testing

---

## 🔧 Example API Call (React)

```typescript
import axios from 'axios';

const API = 'http://localhost:5000/api/competitions';

// Create competition
const response = await axios.post(API, {
  season_id: 'uuid',
  name: 'County Championship',
  stage_level: 'county',
  format_type: 'knockout',
  legs: 1,
  county_id: 'uuid'
});

// Get competition with standings
const data = await axios.get(`${API}/{id}`);
const { competition, standings } = data.data;

// Add teams
await axios.post(`${API}/{id}/teams`, {
  team_ids: ['uuid1', 'uuid2', 'uuid3']
});

// Generate fixtures
await axios.post(`${API}/{id}/generate-fixtures`, {
  start_date: '2024-03-01T00:00:00Z',
  days_between_matches: 7
});
```

---

## 🎨 UI Layout Suggestion

```
┌─────────────────────────────────────────┐
│           PlayerSphere                  │
│     Competition Management              │
├────────────┬────────────────────────────┤
│ Sidebar    │  Main Content              │
│            │                            │
│ Seasons    │  ┌──────────────────────┐ │
│ - 2024     │  │   Competitions List   │ │
│   - County │  │                      │ │
│   - Region │  │  [Create New]        │ │
│   - Nation │  │                      │ │
│            │  │  [Competition Card]  │ │
│            │  │  [Competition Card]  │ │
│            │  │  [Competition Card]  │ │
│            │  └──────────────────────┘ │
└────────────┴────────────────────────────┘

Competition Detail Tabs:
┌──────────────────────────────────────────┐
│ Overview │ Teams │ Fixtures │ Standings │
├──────────────────────────────────────────┤
│                                          │
│         [Tab Content Here]               │
│                                          │
└──────────────────────────────────────────┘
```

---

## 🔗 API Integration Checklist

- [ ] Install axios or use fetch
- [ ] Create `api/competitionApi.ts` service
- [ ] Setup base URL configuration
- [ ] Add error handling middleware
- [ ] Create TypeScript types (see FRONTEND_INTEGRATION_GUIDE.md)
- [ ] Implement Context/Redux store
- [ ] Test each endpoint with sample data
- [ ] Build components in order
- [ ] Add loading states
- [ ] Add error boundary

---

## 📊 Sample Responses (Real API Format)

**GET /competitions**
```json
[
  {
    "id": "uuid",
    "name": "Nairobi County",
    "stage_level": "county",
    "format_type": "knockout",
    "status": "draft",
    "team_count": 150
  }
]
```

**GET /competitions/{id}/standings**
```json
[
  {
    "team_id": "uuid",
    "team_name": "Team A",
    "played": 5,
    "wins": 3,
    "points": 10,
    "goal_difference": 4
  }
]
```

---

## ⚙️ Configuration

- **Local Dev:** `http://localhost:5000/api/competitions`
- **Staging:** `https://staging-api.playersphere.com/api/competitions`
- **Production:** `https://api.playersphere.com/api/competitions`

---

## 🆘 Common Scenarios to Handle

1. **Create a tournament** → Add teams → Generate fixtures → View standings
2. **County to Regional** → View eligible teams → Auto-advance → Verify in new tournament
3. **Emergency adjustment** → Manual advance specific teams → Apply rules
4. **200-team county** → Knockout format → Backend auto-generates preliminaries
5. **Live score update** → Teams see standings update in real-time

---

## 🔐 Auth (Placeholder)

All endpoints require auth headers:
```typescript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

Implementation note: Auth decorators exist on backend, frontend must include Bearer token in all requests.

---

## 📚 Full Documentation Files

For detailed information, read these files in the backend repo:

1. **FRONTEND_INTEGRATION_GUIDE.md** ← START HERE (complete endpoint reference)
2. **COMPETITION_ENGINE_GUIDE.md** (architecture & concepts)
3. **COMPETITION_ENGINE_API.md** (quick API reference)
4. **COMPETITION_ENGINE_README.md** (overview)

---

## ✨ What Makes This Special

✅ **Flexible Tournament Formats**
- Knockout (handles 200+ teams with automatic preliminaries)
- Round Robin (all vs all)
- Group + Knockout (group stage then knockout finals)

✅ **Multiple Stages**
- County, Regional, National (or any custom)
- Auto-advance or manual override

✅ **Configurable Points System**
- Win/Draw/Loss points per competition
- Dynamic standings calculation

✅ **No Time Constraint**
- Manual advancement for emergency scenarios
- Fully flexible advancement control

---

## 🎯 Getting Started Right Now

1. **Read:** `FRONTEND_INTEGRATION_GUIDE.md` (10 min read)
2. **Understand:** Data models & API structure
3. **Setup:** Create API service file
4. **Build:** Start with Competition List component
5. **Connect:** Wire up first API call
6. **Iterate:** Add more components

---

## 💡 Pro Tips

- Test each endpoint with curl/Postman before building UI
- Create sample data/fixtures for testing
- Use TypeScript for type safety
- Implement loading & error states early
- Build reusable components (cards, tables, forms)
- Start with MVP (create, list, view, add teams)
- Add advanced features (advancement, rules) last

---

## 📞 Questions?

**Full reference:** `FRONTEND_INTEGRATION_GUIDE.md`  
**API examples:** See endpoint reference in that document  
**TypeScript types:** Included in integration guide  

Backend team is ready to support during integration.

---

## ✅ Success Criteria

Frontend is complete when you can:
- ✓ Create a competition
- ✓ Add teams
- ✓ Generate fixtures
- ✓ View standings
- ✓ Advance teams
- ✓ All 16 endpoints consumed
- ✓ Error handling working
- ✓ UI is responsive

**Current Backend Status:** 🟢 **READY FOR FRONTEND INTEGRATION**

All endpoints tested and production-ready. API documentation complete.
