# currency.py - convert foreign currency claims to INR

RATES = {}


def set_rates(r):
    global RATES
    RATES = r


def to_inr(amount, currency, month):
    if currency == "INR":
        return amount
    if not month in RATES:
        raise Exception("No exchange rates for " + month)
    if not currency in RATES[month]:
        raise Exception("No rate for " + currency + " in " + month)
    return round(amount * RATES[month][currency], 2)
