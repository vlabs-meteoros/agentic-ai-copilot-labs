"""The expense policy rules (policy v3, April 2025): city tiers, limits and receipts."""

TIER1_CITIES = {"bengaluru", "chennai", "delhi", "hyderabad", "kolkata", "mumbai", "pune"}

NO_LIMIT = -1           # get_limit() returns this for categories without a limit
RECEIPT_THRESHOLD = 500  # INR

# grade -> (tier 1 limit, tier 2 limit), in INR
MEAL_LIMITS_PER_DAY = {
    "G1": (600, 450),
    "G2": (800, 600),
    "G3": (1000, 800),
    "G4": (1500, 1200),
}
HOTEL_LIMITS_PER_NIGHT = {
    "G1": (3000, 2000),
    "G2": (4000, 3000),
    "G3": (6000, 4500),
    "G4": (9000, 7000),
}
GRADE_LIMITS = {"MEAL": MEAL_LIMITS_PER_DAY, "HOTEL": HOTEL_LIMITS_PER_NIGHT}
FLAT_LIMITS = {"INTERNET": 1000, "OTHER": 2000, "TRAVEL": NO_LIMIT}


def get_tier(city: str, currency: str) -> int:
    """Return the city tier (1 or 2); foreign-currency claims are overseas and count as tier 1."""
    if currency != "INR" or city.lower() in TIER1_CITIES:
        return 1
    return 2


def get_limit(category: str, grade: str, tier: int) -> int:
    """Return the INR limit for a category, grade and tier; NO_LIMIT (-1) for TRAVEL, 0 if unknown."""
    if category in FLAT_LIMITS:
        return FLAT_LIMITS[category]
    by_grade = GRADE_LIMITS.get(category, {})
    if grade not in by_grade:
        return 0
    tier1_limit, tier2_limit = by_grade[grade]
    return tier1_limit if tier == 1 else tier2_limit


def needs_receipt(amount: float) -> bool:
    """Return True if a claim of this INR amount needs a receipt."""
    return amount >= RECEIPT_THRESHOLD
