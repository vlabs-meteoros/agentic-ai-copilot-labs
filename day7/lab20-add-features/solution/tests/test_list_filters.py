"""KA-101: list --free and --city."""
from kaveriassets.cli import main


def ids(out: str) -> list[str]:
    """The asset ids in the list output (the last line is the count)."""
    return [line.split()[0] for line in out.splitlines()[:-1]]


def test_free_assets_in_mysuru_any_case(capsys, data_dir):
    assert main(["--data", str(data_dir), "list", "--free", "--city", "mysuru"]) == 0
    out = capsys.readouterr().out
    assert ids(out) == ["KA-H002", "KA-L005", "KA-L006", "KA-L007", "KA-M002"]
    assert out.splitlines()[-1] == "5 asset(s)"


def test_filters_combine_with_type(capsys, data_dir):
    main(["--data", str(data_dir), "list", "--type", "laptop", "--free", "--city", "Bengaluru"])
    assert ids(capsys.readouterr().out) == ["KA-L008"]


def test_city_on_its_own(capsys, data_dir):
    main(["--data", str(data_dir), "list", "--city", "BENGALURU"])
    assert ids(capsys.readouterr().out) == ["KA-H003", "KA-L008", "KA-L009", "KA-L011", "KA-M004", "KA-P001", "KA-P002"]


def test_unknown_city_matches_nothing(capsys, data_dir):
    main(["--data", str(data_dir), "list", "--city", "Pune"])
    assert capsys.readouterr().out.strip() == "No assets match."


def test_free_and_status_together_is_a_usage_error(capsys, data_dir):
    import pytest
    with pytest.raises(SystemExit) as stop:
        main(["--data", str(data_dir), "list", "--free", "--status", "assigned"])
    assert stop.value.code == 2


def test_service_city_filter(service):
    assert [a.asset_id for a in service.list_assets(type="phone", city=" bengaluru ")] == ["KA-P001", "KA-P002"]
