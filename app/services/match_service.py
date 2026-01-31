# app/services/match_service.py
from app.extensions.db import db
from app.models.match import Match, MatchStatus
from app.models.match_event import MatchEvent
from app.models.enums import EventType
from datetime import datetime, timedelta

def schedule_match(data, coach_id):
    """
    Creates a new match in scheduled state.
    """
    match = Match(
        home_team_id=data["home_team_id"],
        away_team_id=data["away_team_id"],
        match_date=data["match_date"],
        venue=data.get("venue"),
        competition=data.get("competition"),
        country=data.get("country"),
        region=data.get("region"),
        city=data.get("city"),
        created_by=coach_id,
        status=MatchStatus.scheduled,
        home_score=0,
        away_score=0,
        current_minute=0
    )
    db.session.add(match)
    db.session.commit()
    return match


def start_match(match: Match):
    """
    Set match status to live and reset current_minute.
    """
    from datetime import datetime
    match.status = MatchStatus.live
    match.current_minute = 1  # Start at minute 1
    match.started_at = datetime.utcnow()
    db.session.commit()
    return match


def finish_match(match: Match):
    """
    Set match status to finished and update team/player stats.
    """
    from app.models.team_stats import TeamStats
    from app.models.player_stats import PlayerStats
    from app.models.player import Player

    print(f"Finishing match {match.id}, current status: {match.status}")
    if match.status != MatchStatus.live:
        raise ValueError("Match is not live")
    match.status = MatchStatus.finished
    from datetime import datetime

    match.started_at = None      # ⛔ stops frontend timers
    match.ended_at = datetime.utcnow()
    match.current_minute = match.current_minute or 90
    print(f"Match {match.id} status set to: {match.status}")
    
    try:
        # Update team stats
        home_team_stats = TeamStats.query.filter_by(team_id=match.home_team_id).first()
        away_team_stats = TeamStats.query.filter_by(team_id=match.away_team_id).first()

        if not home_team_stats:
            home_team_stats = TeamStats(team_id=match.home_team_id)
            db.session.add(home_team_stats)

        if not away_team_stats:
            away_team_stats = TeamStats(team_id=match.away_team_id)
            db.session.add(away_team_stats)

        # Update match counts
        home_team_stats.matches_played += 1
        away_team_stats.matches_played += 1

        # Update goals
        home_team_stats.goals_for += match.home_score
        home_team_stats.goals_against += match.away_score
        away_team_stats.goals_for += match.away_score
        away_team_stats.goals_against += match.home_score

        # Update wins/draws/losses
        if match.home_score > match.away_score:
            home_team_stats.wins += 1
            away_team_stats.losses += 1
        elif match.home_score < match.away_score:
            away_team_stats.wins += 1
            home_team_stats.losses += 1
        else:
            home_team_stats.draws += 1
            away_team_stats.draws += 1

        # Update clean sheets
        if match.away_score == 0:
            home_team_stats.clean_sheets += 1
        if match.home_score == 0:
            away_team_stats.clean_sheets += 1

        # Update player stats
        for event in match.events:
            if event.player_id:
                player_stats = PlayerStats.query.filter_by(player_id=event.player_id).first()
                if not player_stats:
                    player_stats = PlayerStats(player_id=event.player_id)
                    db.session.add(player_stats)

                ev_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)

                if ev_type in ['goal', 'penalty_goal']:
                    player_stats.goals += 1
                elif ev_type == 'yellow_card':
                    player_stats.yellow_cards += 1
                elif ev_type == 'red_card':
                    player_stats.red_cards += 1

        # Increment matches_played and minutes_played for players who participated (had events)
        player_ids = {e.player_id for e in match.events if e.player_id}
        for pid in player_ids:
            ps = PlayerStats.query.filter_by(player_id=pid).first()
            if ps:
                ps.matches_played += 1
                try:
                    ps.minutes_played += int(match.current_minute or 0)
                except Exception:
                    ps.minutes_played += 0

                # Count matches played (if not already counted)
                # This is a simple implementation - in reality you'd track unique matches per player

    except Exception as e:
        # Log the error but don't fail the match finishing
        print(f"Error updating stats for match {match.id}: {e}")
        # Continue with committing the match status change

    print(f"Committing match {match.id} with status: {match.status}")
    db.session.commit()
    print(f"Match {match.id} finished successfully")
    return match


def compute_score(match: Match):
    """
    Compute match score based on logged GOAL events.
    Ensures a single source of truth for scores.
    """
    home = 0
    away = 0

    # Use relationship: match.events
    for event in match.events:
        ev_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
        if ev_type == "goal":
            if event.team_id == match.home_team_id:
                home += 1
            else:
                away += 1

    return home, away


def create_tournament_matches(tournament_id, matches_data):
    """
    Bulk create matches for a tournament.
    """
    created_matches = []

    for data in matches_data:
        match = Match(
            competition=str(tournament_id),
            home_team_id=data["home_team_id"],
            away_team_id=data["away_team_id"],
            match_date=data["match_date"],
            venue=data.get("venue"),
            status=MatchStatus.scheduled,
            home_score=0,
            away_score=0,
            current_minute=0,
        )
        db.session.add(match)
        created_matches.append(match)

    db.session.commit()
    return [m.to_dict() for m in created_matches]


def generate_round_robin(tournament_id, team_ids, start_date_iso, interval_days=7, venue=None):
    """
    Simple round-robin generator.
    - `team_ids`: list of team UUID strings
    - `start_date_iso`: ISO date string for first round
    - `interval_days`: days between rounds (default 7)
    Returns list of created match dicts.
    """
    # Parse start date
    try:
        start_dt = datetime.fromisoformat(start_date_iso)
    except Exception:
        # Fallback: treat as UTC naive parse
        start_dt = datetime.strptime(start_date_iso, "%Y-%m-%dT%H:%M:%S")

    teams = list(team_ids)
    if len(teams) < 2:
        return []

    # If odd, add a bye (None)
    bye = None
    if len(teams) % 2 == 1:
        teams.append(bye)

    n = len(teams)
    rounds = n - 1
    matches_created = []

    # Use standard round-robin algorithm (circle method)
    roster = teams[:]
    fixed = roster[0]
    others = roster[1:]

    for r in range(rounds):
        round_date = start_dt + timedelta(days=r * interval_days)
        # Build left and right lists for pairing
        left = [fixed] + others[:(n//2 - 1)]
        right = list(reversed(others[(n//2 - 1):]))

        for i in range(n // 2):
            home = left[i] if i < len(left) else None
            away = right[i] if i < len(right) else None
            if home is None or away is None:
                # bye or unmatched
                continue

            match = Match(
                home_team_id=home,
                away_team_id=away,
                match_date=round_date,
                venue=venue,
                competition=str(tournament_id),
                status=MatchStatus.scheduled,
                home_score=0,
                away_score=0,
                current_minute=0,
            )
            db.session.add(match)
            matches_created.append(match)

        # rotate the others for next round
        others = [others[-1]] + others[:-1]

    db.session.commit()
    return [m.to_dict() for m in matches_created]