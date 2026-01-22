from datetime import date

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )


def player_age_group(player):
    age = calculate_age(player.date_of_birth)

    if age <= 15:
        return "U15"
    if age <= 17:
        return "U17"
    return "SENIOR"
