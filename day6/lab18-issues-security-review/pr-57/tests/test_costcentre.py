from kavericlaims import costcentre


def test_summarise_returns_a_dict(capsys):
    assert costcentre.main(["--month", "2026-11"]) == 0
    assert "COST CENTRES" in capsys.readouterr().out


def test_fmt_inr():
    assert costcentre.fmt_inr(1234567.5) == "1,234,567.50"
