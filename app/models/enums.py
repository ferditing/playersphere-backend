import enum

class MatchStatus(enum.Enum):
    scheduled = "scheduled"
    live = "live"
    finished = "finished"
    cancelled = "cancelled"

class EventType(enum.Enum):
    goal = "goal"
    penalty_goal = "penalty_goal"
    own_goal = "own_goal"
    yellow_card = "yellow_card"
    red_card = "red_card"
    substitution = "substitution"

class MatchInterestStatus(enum.Enum):
    pending  = "pending"
    accepted = "accepted"
    declined = "declined"