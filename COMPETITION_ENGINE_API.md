# Competition Engine - API Quick Reference

## Base URL
All endpoints are prefixed with `/api/competitions/`

## Competition CRUD

### Create Competition
```
POST /api/competitions
Content-Type: application/json

{
  "season_id": "uuid",
  "name": "Nairobi County Championship",
  "stage_level": "county",
  "format_type": "knockout",
  "legs": 1,
  "region_id": "uuid (optional)",
  "county_id": "uuid (optional)",
  "max_teams": 200,
  "min_teams": 2,
  "points_win": 3,
  "points_draw": 1,
  "points_loss": 0
}

Response: 201 Created
{
  "id": "...",
  "season_id": "...",
  "name": "...",
  "stage_level": "county",
  "format_type": "knockout",
  ...
}
```

### List Competitions
```
GET /api/competitions?season_id=uuid&stage_level=county&status=ongoing

Response: 200 OK
[
  {
    "id": "...",
    "name": "Nairobi County Championship",
    "stage_level": "county",
    "format_type": "knockout",
    "status": "draft",
    "team_count": 150,
    ...
  }
]
```

### Get Competition Details
```
GET /api/competitions/{id}

Response: 200 OK
{
  "competition": {
    "id": "...",
    "name": "...",
    "team_count": 150,
    "match_count": 75,
    ...
  },
  "standings": [
    {
      "team_id": "...",
      "team_name": "Team A",
      "played": 5,
      "wins": 3,
      "draws": 1,
      "losses": 1,
      "points": 10,
      "goals_for": 12,
      "goals_against": 8,
      "goal_difference": 4
    }
  ]
}
```

### Update Competition
```
PATCH /api/competitions/{id}
Content-Type: application/json

{
  "name": "New Name",
  "status": "ongoing",
  "max_teams": 300,
  "points_win": 4
}

Response: 200 OK
```

## Team Management

### Add Teams (Auto-qualified)
```
POST /api/competitions/{id}/teams
Content-Type: application/json

{
  "team_ids": ["uuid1", "uuid2", "uuid3"]
}

Response: 201 Created
{
  "added_count": 3,
  "teams": [
    {
      "id": "...",
      "team_id": "uuid1"
    }
  ]
}
```

### Add Teams (Manual Override)
```
POST /api/competitions/{id}/teams/manual
Content-Type: application/json

{
  "team_ids": ["uuid1", "uuid2"]
}

Response: 201 Created
{
  "added_count": 2,
  "teams": [
    {
      "id": "...",
      "team_id": "uuid1",
      "manually_added": true
    }
  ]
}
```

### List Teams in Competition
```
GET /api/competitions/{id}/teams

Response: 200 OK
[
  {
    "id": "...",
    "team_id": "...",
    "team_name": "Team A",
    "manually_added": false,
    "seeded_position": 1,
    "group_id": "uuid or null"
  }
]
```

## Fixtures & Schedule

### Generate Fixtures
```
POST /api/competitions/{id}/generate-fixtures
Content-Type: application/json

{
  "start_date": "2024-03-01T00:00:00Z",
  "days_between_matches": 7,
  "num_groups": 4
}

Response: 201 Created
{
  "generated_matches": 45,
  "format_type": "group_knockout",
  "matches": [
    {
      "id": "...",
      "home_team_id": "...",
      "away_team_id": "...",
      "match_date": "2024-03-01T...",
      "status": "scheduled"
    }
  ]
}
```

### Get Fixtures
```
GET /api/competitions/{id}/fixtures?group_id=uuid&knockout_round_id=uuid

Response: 200 OK
[
  {
    "id": "...",
    "home_team_id": "...",
    "home_team": { ... },
    "away_team_id": "...",
    "away_team": { ... },
    "match_date": "...",
    "venue": "...",
    "status": "scheduled",
    "home_score": 0,
    "away_score": 0
  }
]
```

## Standings

### Get Standings
```
GET /api/competitions/{id}/standings

Response: 200 OK
[
  {
    "team_id": "...",
    "team_name": "Team A",
    "played": 5,
    "wins": 3,
    "draws": 1,
    "losses": 1,
    "points": 10,
    "goals_for": 12,
    "goals_against": 8,
    "goal_difference": 4,
    "seeded_position": 1
  }
]
```

## Advancement & Qualification

### Get Eligible Teams for Advancement
```
GET /api/competitions/{from_id}/to/{to_id}/eligible-teams

Response: 200 OK
[
  {
    "team_id": "...",
    "team_name": "Team A",
    "position": 1,
    "points": 10
  }
]
```

### Auto-Advance Teams (by standings)
```
POST /api/competitions/{from_id}/advance-to/{to_id}
Content-Type: application/json

{
  "num_positions": 4
}

Response: 200 OK
{
  "advanced_count": 4,
  "teams": [
    { "team_id": "..." }
  ]
}
```

### Manual Advancement (Override)
```
POST /api/competitions/{from_id}/advance-manual/{to_id}
Content-Type: application/json

{
  "team_ids": ["uuid1", "uuid2", "uuid3"]
}

Response: 200 OK
{
  "advanced_count": 3,
  "teams": [
    { "team_id": "uuid1" }
  ],
  "note": "Teams added via manual override"
}
```

### Apply Advancement Rules
```
POST /api/competitions/{id}/apply-rules

Response: 200 OK
{
  "total_rules": 2,
  "results": [
    {
      "rule_id": "...",
      "rule_type": "top_positions",
      "status": "success",
      "result": {
        "advanced_count": 4,
        "teams": [...]
      }
    },
    {
      "rule_id": "...",
      "rule_type": "group_winners",
      "status": "success",
      "result": {
        "advanced_count": 4,
        "teams": [...]
      }
    }
  ]
}
```

### Get Advancement Summary
```
GET /api/competitions/{from_id}/advancement-summary?to_id=uuid

Response: 200 OK
{
  "from_competition": {
    "id": "...",
    "name": "Nairobi County Championship",
    "stage_level": "county",
    "format_type": "knockout"
  },
  "advancement_rules": [
    {
      "rule_id": "...",
      "rule_type": "knockout_winner",
      "advancement_positions": null,
      "auto_apply": true,
      "to_competition_id": "...",
      "eligible_teams_count": 1,
      "eligible_teams": [
        {
          "team_id": "...",
          "team_name": "Team A",
          "points": 10
        }
      ]
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 404 Not Found
```json
{
  "error": "Competition not found"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error message"
}
```

## Format Types Reference

### round_robin
- All teams play against each other
- Supports 1 or 2 legs
- Use for regional/national stages with limited teams (max ~12)

### knockout
- Single-elimination format
- Can handle 200+ teams (generates preliminary rounds automatically)
- Best for county stages
- Supports 1 or 2 legs in finals

### group_knockout
- Group stage (all vs all within groups)
- Then group-winners advance to knockout
- Best for regional/national stages
- Configurable number of groups

## Rule Types Reference

### top_positions
- Auto-advance top N teams by standings
- Use: advancement_positions field
- Example: Top 4 from county → regional

### group_winners
- Auto-advance only group winners
- For group_knockout format only
- Example: 4 group winners from regional → nationals

### knockout_winner
- Auto-advance only the tournament winner
- For knockout formats
- Example: County champion → regional

### manual_only
- No auto-advancement, requires manual action
- Useful when advancement is conditional
- Example: Only advance with explicit approval

## Status Values

**Competition Status:**
- `draft` - Not yet active
- `ongoing` - Currently running
- `completed` - Finished

**Match Status:**
- `scheduled` - Not yet played
- `ongoing` - Currently in progress
- `completed` - Finished

**Knockout Round Status:**
- `pending` - Awaiting matches
- `ongoing` - Matches in progress
- `completed` - All matches finished
