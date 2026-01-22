def can_add_event(match, event_type):
    if match.status == "FULL_TIME":
        return False

    if match.status == "NOT_STARTED" and event_type != "KICK_OFF":
        return False

    return True
