from kavericlaims import currency


def test_usd_is_converted_at_the_rate_for_the_month():
    currency.RATES = {"2026-11": {"USD": 84.20}}
    assert currency.to_inr(10.0, "USD", "2026-11") == 842.0


def test_inr_is_not_converted():
    assert currency.to_inr(123.45, "INR", "2026-11") == 123.45
