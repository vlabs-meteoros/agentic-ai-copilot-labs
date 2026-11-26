"""Tests for the command-line interface (kaveriassets.cli)."""
from kaveriassets.cli import main


def run(capsys, data_dir, *args):
    """Run the CLI on the temporary data. Returns (exit code, stdout, stderr)."""
    code = main(["--data", str(data_dir), *args])
    out, err = capsys.readouterr()
    return code, out, err


def test_list_free_laptops(capsys, data_dir):
    code, out, _ = run(capsys, data_dir, "list", "--type", "laptop", "--status", "in_stock")
    assert code == 0
    assert out.splitlines()[0] == "KA-L005  laptop   Dell Latitude 5450          Mysuru     in_stock"
    assert out.splitlines()[-1] == "4 asset(s)"


def test_show_an_assigned_asset(capsys, data_dir):
    code, out, _ = run(capsys, data_dir, "show", "KA-L001")
    assert code == 0
    assert "Status:    assigned to Ananya Iyer (E01, Payments)" in out


def test_assign_then_return(capsys, data_dir):
    code, out, _ = run(capsys, data_dir, "assign", "KA-L006", "E07", "--today", "2026-12-01")
    assert (code, out.strip()) == (0, "Assigned KA-L006 (Lenovo ThinkPad T14 Gen 5) to Divya Hegde (E07)")
    code, out, _ = run(capsys, data_dir, "return", "KA-L006", "--today", "2026-12-02")
    assert (code, out.strip()) == (0, "Returned KA-L006 (Lenovo ThinkPad T14 Gen 5) to stock in Mysuru")


def test_a_refusal_is_an_error_message_and_exit_code_1(capsys, data_dir):
    code, out, err = run(capsys, data_dir, "assign", "KA-L008", "E07")
    assert code == 1
    assert out == ""
    assert err.startswith("Error: KA-L008 is in Bengaluru")
