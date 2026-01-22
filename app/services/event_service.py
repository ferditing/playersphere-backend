from app.extensions import db
from app.models.match_event import MatchEvent
from app.models.match import MatchStatus
from app.services.match_service import compute_score


def log_event(match, data):
    if match.status != MatchStatus.live:
        raise ValueError("Match is not live")

    event = MatchEvent(
        match_id=match.id,
        team_id=data["team_id"],
        player_id=data.get("player_id"),
        event_type=data["event_type"],
        minute=data["minute"],
        additional_info=data.get("additional_info", {})
    )

    db.session.add(event)
    db.session.flush()  # make event visible before computing score

    # ✅ single source of truth
    home, away = compute_score(match)
    match.home_score = home
    match.away_score = away

    match.current_minute = data["minute"]

    db.session.commit()
    return event
