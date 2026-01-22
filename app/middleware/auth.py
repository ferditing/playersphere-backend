from flask import g, abort
from app.models.coach import Coach

def require_coach():
    coach_id = getattr(g, "coach_id", None)
    if not coach_id:
        abort(401, "Unauthorized")

    coach = Coach.query.get(coach_id)
    if not coach:
        abort(401, "Invalid coach")

    g.current_coach = coach
