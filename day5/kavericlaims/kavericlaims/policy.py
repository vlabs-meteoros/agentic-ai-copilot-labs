# policy.py - the expense policy rules
# limits updated for policy v3 (April 2025)

TIER1 = ["Bengaluru", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai", "Pune"]


def get_tier(city, currency):
    if currency != "INR":
        return 1
    for c in TIER1:
        if c.lower() == city.lower():
            return 1
    return 2


def get_limit(category, grade, tier):
    if category == "MEAL":
        if grade == "G1":
            if tier == 1:
                return 600
            else:
                return 450
        elif grade == "G2":
            if tier == 1:
                return 800
            else:
                return 600
        elif grade == "G3":
            if tier == 1:
                return 1000
            else:
                return 600
        elif grade == "G4":
            if tier == 1:
                return 1500
            else:
                return 1200
    elif category == "HOTEL":
        if grade == "G1":
            if tier == 1:
                return 3000
            else:
                return 2000
        elif grade == "G2":
            if tier == 1:
                return 4000
            else:
                return 3000
        elif grade == "G3":
            if tier == 1:
                return 6000
            else:
                return 4500
        elif grade == "G4":
            if tier == 1:
                return 9000
            else:
                return 7000
    elif category == "INTERNET":
        return 1000
    elif category == "OTHER":
        return 2000
    elif category == "TRAVEL":
        return -1  # -1 = no limit
    return 0


def needs_receipt(amount):
    if amount > 500:
        return True
    return False
