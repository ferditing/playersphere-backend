# Competition Engine Guide

## Overview

The Competition Engine is a fully modular, configurable system for managing tournaments and competitions with multiple formats, stages, and advancement rules. It's designed to handle any tournament structure without hardcoding league-specific logic.

## Core Architecture

### 1. Models

#### **Competition**
The central entity that defines a tournament with all its configuration.

**Key Fields:**
- `season_id` - Links to the season (FK)
- `name` - Competition name (unique per season)
- `stage_level` - 'county' | 'regional' | 'national'
- `format_type` - 'round_robin' | 'knockout' | 'group_knockout'
- `legs` - 1 (single leg) or 2 (double leg)
- `points_win/draw/loss` - Fully configurable points for each outcome
- `region_id / county_id` - Optional location constraints
- `status` - 'draft' | 'ongoing' | 'completed'
- `max_teams / min_teams` - Team limits

**Relationships:**
- `teams` → CompetitionTeam (all teams in this competition)
- `groups` → CompetitionGroup (for group-based formats)
- `knockout_rounds` → KnockoutRound (for knockout formats)
- `matches` → Match (all matches in this competition)
- `advancement_rules_from` → CompetitionAdvancementRule (rules originating from this comp)
- `advancement_rules_to` → CompetitionAdvancementRule (rules pointing to this comp)

#### **CompetitionTeam**
Links teams to competitions with qualification tracking.

**Key Fields:**
- `competition_id` - FK to Competition
- `team_id` - FK to Team
- `manually_added` - Boolean flag for override qualification
- `seeded_position` - Initial ranking for bracket seeding
- `group_id` - FK to CompetitionGroup (optional, for group-based formats)

**Constraint:** Unique (competition_id, team_id) - prevents duplicate team entries

#### **CompetitionGroup**
Represents groups in group-based competitions.

**Key Fields:**
- `competition_id` - FK to Competition
- `name` - "Group A", "Group B", etc.
- `group_order` - Ordering of groups

#### **KnockoutRound**
Represents rounds in knockout-based competitions.

**Key Fields:**
- `competition_id` - FK to Competition
- `round_name` - "Quarter-Finals", "Semi-Finals", "Final", etc.
- `round_order` - Chronological order (1, 2, 3...)
- `matches_per_pairing` - 1 or 2 legs
- `status` - 'pending' | 'ongoing' | 'completed'

#### **CompetitionAdvancementRule**
Defines how teams advance from one competition to the next.

**Key Fields:**
- `from_competition_id` - Source competition
- `to_competition_id` - Destination competition (optional)
- `rule_type` - 'top_positions' | 'group_winners' | 'knockout_winner' | 'manual_only'
- `advancement_positions` - Number of teams for 'top_positions'
- `auto_apply` - Whether to auto-execute or require manual trigger

**Constraint:** Unique (from_competition_id, rule_type)

#### **Match** (Updated)
Updated to link to competition structure.

**New Fields:**
- `competition_id` - FK to Competition (links match to specific tournament)
- `group_id` - FK to CompetitionGroup (optional, for group-stage matches)
- `knockout_round_id` - FK to KnockoutRound (optional, for knockout matches)

## Services

### 1. CompetitionService

**Competition Management:**
```python
# Create a competition
comp = CompetitionService.create_competition(
    season_id=season_id,
    name="County Championship",
    stage_level="county",
    format_type="knockout",
    legs=1,
    points_win=3,
    points_draw=1,
    points_loss=0,
    county_id=county_id
)

# Add teams automatically (e.g., qualified teams)
teams = CompetitionService.add_teams_auto(comp.id, [team1_id, team2_id])

# Manually override team addition
teams = CompetitionService.add_teams_manual(comp.id, [team3_id, team4_id])
```

**Standings & Calculations:**
```python
# Get competition standings (sorted by points, goal diff, goals for)
standings = CompetitionService.get_competition_standings(comp.id)

# Returns:
# [
#   {
#     'team_id': '...',
#     'team_name': 'Team A',
#     'played': 5,
#     'wins': 3,
#     'draws': 1,
#     'losses': 1,
#     'points': 10,
#     'goals_for': 12,
#     'goals_against': 8,
#     'goal_difference': 4,
#     'seeded_position': 1
#   },
#   ...
# ]
```

**Advancement Rules:**
```python
# Create advancement rule (auto-advance top 4 teams)
rule = CompetitionService.create_advancement_rule(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id,
    rule_type='top_positions',
    advancement_positions=4,
    auto_apply=True
)

# Get eligible teams for advancement
eligible = CompetitionService.get_eligible_teams_for_advancement(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id
)
```

### 2. SchedulingService

**Generate Fixtures:**
```python
# Round Robin (all vs all, 1 or 2 legs)
matches = SchedulingService.generate_round_robin_fixtures(
    competition_id=comp.id,
    days_between_matches=7,
    legs=1
)

# Knockout (200 teams in county scenario)
matches = SchedulingService.generate_knockout_brackets(
    competition_id=comp.id,
    days_between_rounds=14
)

# Group Knockout (group stage + knockout)
matches = SchedulingService.generate_group_knockout_fixtures(
    competition_id=comp.id,
    groups_config=4,  # 4 groups
    days_between_matches=7
)

# Reschedule
updated = SchedulingService.reschedule_matches(
    competition_id=comp.id,
    start_date=new_start_date,
    days_between_matches=7
)

# Get schedule
schedule = SchedulingService.get_schedule(
    competition_id=comp.id,
    group_id=group_id,  # optional
    knockout_round_id=round_id  # optional
)
```

### 3. AdvancementService

**Auto-Advancement:**
```python
# Advance top N by standings
result = AdvancementService.advance_teams_by_standings(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id,
    num_positions=4
)

# Advance group winners (group_knockout format)
result = AdvancementService.advance_group_winners(
    from_competition_id=regional_comp.id,
    to_competition_id=national_comp.id
)

# Advance knockout winner
result = AdvancementService.advance_knockout_winner(
    from_competition_id=national_comp.id,
    to_competition_id=champions_league.id
)
```

**Manual Advancement:**
```python
# Emergency override - add teams manually to next tier
result = AdvancementService.advance_teams_manually(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id,
    team_ids=[team1_id, team2_id, team3_id, team4_id]
)
```

**Apply Rules:**
```python
# Execute all advancement rules for a competition
results = AdvancementService.apply_advancement_rules(
    from_competition_id=county_comp.id
)

# Returns status for each rule: success, error, skipped
```

**Advancement Summary:**
```python
# Get full advancement context
summary = AdvancementService.get_advancement_summary(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id  # optional
)
```

## API Routes

### Competition Management
```
POST   /api/competitions                    - Create competition
GET    /api/competitions                    - List competitions (filter by season, stage)
GET    /api/competitions/<id>               - Get competition details with standings
PATCH  /api/competitions/<id>               - Update competition config
```

### Team Management
```
POST   /api/competitions/<id>/teams         - Add teams (auto-qualified)
POST   /api/competitions/<id>/teams/manual  - Add teams (manual override)
GET    /api/competitions/<id>/teams         - List teams in competition
```

### Fixtures
```
POST   /api/competitions/<id>/generate-fixtures  - Generate fixtures
GET    /api/competitions/<id>/fixtures           - Get schedule
```

### Standings & Results
```
GET    /api/competitions/<id>/standings    - Get current standings
```

### Advancement
```
GET    /api/competitions/<from_id>/to/<to_id>/eligible-teams        - Get eligible teams
POST   /api/competitions/<from_id>/advance-to/<to_id>               - Auto-advance top N
POST   /api/competitions/<from_id>/advance-manual/<to_id>           - Manual override
POST   /api/competitions/<id>/apply-rules                           - Apply all rules
GET    /api/competitions/<from_id>/advancement-summary              - Get summary
```

## Usage Examples

### Scenario 1: County Championship (200 teams, knockout)

```python
# 1. Create competition
county_comp = CompetitionService.create_competition(
    season_id=season_id,
    name="Nairobi County Championship",
    stage_level="county",
    format_type="knockout",
    legs=1,
    county_id=nairobi_county_id,
    max_teams=200
)

# 2. Add teams (auto-qualified by criteria)
teams_to_add = fetch_teams_by_county_criteria()
CompetitionService.add_teams_auto(county_comp.id, team_ids)

# 3. Generate fixtures (handles prelims automatically)
matches = SchedulingService.generate_knockout_brackets(
    competition_id=county_comp.id,
    days_between_rounds=14
)

# 4. Define advancement rule to regional
rule = CompetitionService.create_advancement_rule(
    from_competition_id=county_comp.id,
    to_competition_id=regional_comp.id,
    rule_type='knockout_winner',
    auto_apply=True
)

# 5. After matches complete, auto-advance winner
AdvancementService.apply_advancement_rules(county_comp.id)
```

### Scenario 2: Regional Championship (Round Robin, then Knockout)

```python
# 1. Create regional competition
regional_comp = CompetitionService.create_competition(
    season_id=season_id,
    name="Western Regional Championship",
    stage_level="regional",
    format_type="group_knockout",
    legs=1,
    region_id=western_region_id
)

# 2. Add qualified teams from county championships
counties_in_region = [nairobi_comp, mombasa_comp, ...]
for county_comp in counties_in_region:
    # Get top 4 from each county
    top_4 = CompetitionService.get_competition_standings(county_comp.id)[:4]
    CompetitionService.add_teams_auto(regional_comp.id, [t['team_id'] for t in top_4])

# 3. Generate group stage + knockout
matches = SchedulingService.generate_group_knockout_fixtures(
    competition_id=regional_comp.id,
    groups_config=4,  # 4 groups
    days_between_matches=7
)

# 4. Create advancement rule for group winners → nationals
rule = CompetitionService.create_advancement_rule(
    from_competition_id=regional_comp.id,
    to_competition_id=national_comp.id,
    rule_type='group_winners',
    auto_apply=True
)
```

### Scenario 3: National Championship with Emergency Adjustments

```python
# 1. Create national competition
national_comp = CompetitionService.create_competition(
    season_id=season_id,
    name="National Championship",
    stage_level="national",
    format_type="group_knockout",
    legs=2,  # Double leg finals
    points_win=3,
    points_draw=1,
    points_loss=0
)

# 2. Auto-advance group winners from each region
for regional_comp in regional_competitions:
    try:
        AdvancementService.advance_group_winners(regional_comp.id, national_comp.id)
    except Exception as e:
        # If a region had issues, manually add their champion
        AdvancementService.advance_teams_manually(
            from_competition_id=regional_comp.id,
            to_competition_id=national_comp.id,
            team_ids=[get_champion(regional_comp.id)]
        )

# 3. Generate group stage
matches = SchedulingService.generate_group_knockout_fixtures(national_comp.id)

# 4. After group stage, advance group winners to knockout finals
AdvancementService.apply_advancement_rules(national_comp.id)
```

## Key Design Principles

1. **Everything is Configuration**
   - Format, stage, points system are all configurable per competition
   - No hardcoded league types (County/Regional/National)
   - Same engine handles all tournament structures

2. **Match Logic Stays Generic**
   - Match model linked via competition_id
   - All match operations use generic fields (group_id, knockout_round_id)
   - Standings calculated per competition's points system

3. **Flexible Advancement**
   - Auto-advancement via standings for most scenarios
   - Manual override for emergency situations
   - Multiple rule types support different advancement patterns

4. **Modular Services**
   - CompetitionService: Orchestration & standings
   - SchedulingService: Fixture generation
   - AdvancementService: Tier-to-tier qualification

5. **No Time Constraint**
   - Manual advancement works when timing issues arise
   - Complete flexibility in advancement pathways

## Migration & Testing

When deploying the Competition Engine:

1. Create a migration for the new tables:
   ```bash
   flask db migrate -m "Add competition engine models"
   flask db upgrade
   ```

2. No data migration needed - existing matches continue to work

3. Run tests:
   ```bash
   python -m pytest tests/services/test_competition_service.py
   python -m pytest tests/services/test_scheduling_service.py
   python -m pytest tests/services/test_advancement_service.py
   ```

## Next Steps

1. **Authentication/Authorization:** Add role-based access to routes
2. **Reporting:** Build dashboards for competition progress
3. **Analytics:** Track advancement patterns, qualification rates
4. **Integrations:** Connect with live scoring, notifications
5. **Performance:** Optimize standings calculation for large datasets
