from app.models.match import Match

class TournamentStatsService:

    @staticmethod
    def matches_played(tournament_id):
        return Match.query.filter_by(
            competition=str(tournament_id),
            status="finished"
        ).count()

    @staticmethod
    def total_goals(tournament_id):
        matches = Match.query.filter_by(
            competition=str(tournament_id),
            status="finished"
        ).all()

        return sum(m.home_score + m.away_score for m in matches)
