from app.extensions import db
from app.models.match_event import MatchEvent
from app.models.player_stats import PlayerStats
from app.models.team_stats import TeamStats

def recompute_player_stats(player_id, season):
    events = MatchEvent.query.filter_by(player_id=player_id).all()

    stats = PlayerStats.query.filter_by(
        player_id=player_id,
        season=season
    ).first()

    if not stats:
        stats = PlayerStats(player_id=player_id, season=season)
        db.session.add(stats)

    stats.goals = sum(1 for e in events if e.event_type == "goal")
    stats.assists = sum(1 for e in events if e.event_type == "assist")
    stats.yellow_cards = sum(1 for e in events if e.event_type == "yellow_card")
    stats.red_cards = sum(1 for e in events if e.event_type == "red_card")

    db.session.commit()
    return stats


def recompute_team_stats(team_id, season):
    stats = TeamStats.query.filter_by(
        team_id=team_id,
        season=season
    ).first()

    if not stats:
        stats = TeamStats(team_id=team_id, season=season)
        db.session.add(stats)

    db.session.commit()
    return stats
