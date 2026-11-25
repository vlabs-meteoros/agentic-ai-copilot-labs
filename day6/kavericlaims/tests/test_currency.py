import pytest

from kavericlaims import currency


def test_usd_is_converted_at_the_rate_for_the_month(rates):
    assert currency.to_inr(10.0, "USD", "2026-11") == 842.0


def test_aed_is_rounded_to_paise(rates):
    assert currency.to_inr(85.0, "AED", "2026-11") == pytest.approx(1949.05)


def test_inr_is_not_converted():
    assert currency.to_inr(123.45, "INR", "2026-11") == 123.45


def test_month_without_rates_raises(rates):
    with pytest.raises(Exception, match="No exchange rates for 2026-12"):
        currency.to_inr(10.0, "USD", "2026-12")


def test_currency_without_a_rate_raises(rates):
    with pytest.raises(Exception, match="No rate for EUR in 2026-11"):
        currency.to_inr(10.0, "EUR", "2026-11")
