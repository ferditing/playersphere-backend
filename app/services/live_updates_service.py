from app.services.standings_service import StandingsService

class LiveUpdatesService:

    @staticmethod
    def on_goal_scored(tournament_id):

        return StandingsService.compute_standings(tournament_id)
    
    @staticmethod
    def on_match_completed(tournament_id):
        return StandingsService.compute_standings(tournament_id)
    
    @staticmethod
    def live_table(tournament_id):
        return StandingsService.compute_standings(tournament_id)