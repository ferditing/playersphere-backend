import uuid
from app.extensions.db import db
from app.models.tournament_invite import TournamentInvite
from app.models.tournament_team import TournamentTeam

class InviteService:

    @staticmethod
    def send_invite(tournament_id, from_coach_id, to_coach_id=None, team_id=None):
        invite = TournamentInvite(
            id=uuid.uuid4(),
            tournament_id=tournament_id,
            from_coach_id=from_coach_id,
            to_coach_id=to_coach_id,
            team_id=team_id,
            status="pending"
        )
        db.session.add(invite)
        db.session.commit()
        return invite

    @staticmethod
    def accept_invite(invite_id):
        invite = TournamentInvite.query.get(invite_id)
        if not invite:
            raise ValueError("Invite not found")

        invite.status = "accepted"
        # If the invite references a team, add the team to the tournament
        if invite.team_id:
            existing = TournamentTeam.query.filter_by(tournament_id=invite.tournament_id, team_id=invite.team_id).first()
            if not existing:
                tt = TournamentTeam(
                    tournament_id=invite.tournament_id,
                    team_id=invite.team_id
                )
                db.session.add(tt)

        db.session.commit()
        return invite

    @staticmethod
    def reject_invite(invite_id):
        invite = TournamentInvite.query.get(invite_id)
        if not invite:
            raise ValueError("Invite not found")

        invite.status = "rejected"
        db.session.commit()
        return invite
