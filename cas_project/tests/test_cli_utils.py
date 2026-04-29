"""
tests/test_cli_utils.py
Unit tests for CLI argument parsing, utils, and logging setup.
"""
import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cas.utils import (
    make_run_id, make_run_dir, stamped_filename,
    write_json, read_json, write_csv, write_manifest
)
from cas.logging_config import setup_logging
from cas.cli import parse_args, build_parser


# ── utils ─────────────────────────────────────────────────────────────────────

def test_run_id_format():
    """Run ID matches expected format run_YYYYMMDD_HHMMSS."""
    import re
    run_id = make_run_id()
    assert re.match(r"run_\d{8}_\d{6}$", run_id), (
        f"Unexpected run_id format: {run_id}"
    )


def test_run_id_custom_prefix():
    run_id = make_run_id("test")
    assert run_id.startswith("test_")


def test_make_run_dir_creates_dir(tmp_path):
    run_dir = make_run_dir(str(tmp_path), "run_test_001")
    assert os.path.isdir(run_dir)
    assert run_dir.endswith("run_test_001")


def test_make_run_dir_idempotent(tmp_path):
    """Calling twice does not raise."""
    make_run_dir(str(tmp_path), "run_dup")
    make_run_dir(str(tmp_path), "run_dup")   # should not raise


def test_stamped_filename(tmp_path):
    path = stamped_filename(str(tmp_path / "run_001"), "report", "html")
    assert path.endswith("report.html")
    assert "run_001" in path


def test_write_and_read_json(tmp_path):
    data = {"key": "value", "numbers": [1, 2, 3]}
    path = str(tmp_path / "sub" / "test.json")
    write_json(data, path)
    assert os.path.exists(path)
    loaded = read_json(path)
    assert loaded == data


def test_write_json_creates_parent_dirs(tmp_path):
    """write_json creates parent directories automatically."""
    path = str(tmp_path / "a" / "b" / "c" / "data.json")
    write_json({"x": 1}, path)
    assert os.path.exists(path)


def test_write_csv(tmp_path):
    rows = [
        {"system": "THAAD", "cost": 12_700_000},
        {"system": "LUCAS", "cost": 35_000},
    ]
    path = str(tmp_path / "out.csv")
    write_csv(rows, path)
    assert os.path.exists(path)
    content = open(path).read()
    assert "THAAD" in content
    assert "LUCAS" in content


def test_write_csv_empty(tmp_path):
    """write_csv handles empty list without raising."""
    write_csv([], str(tmp_path / "empty.csv"))
    # File should not be created for empty data
    assert not os.path.exists(str(tmp_path / "empty.csv"))


def test_write_manifest(tmp_path):
    run_dir = str(tmp_path / "run_001")
    os.makedirs(run_dir)
    path = write_manifest(run_dir, {"version": "1.1.0", "n_sims": 1000})
    assert os.path.exists(path)
    data = json.loads(open(path).read())
    assert data["version"] == "1.1.0"
    assert "generated_at" in data


# ── logging ───────────────────────────────────────────────────────────────────

def test_logging_creates_log_file(tmp_path):
    run_dir = str(tmp_path / "run_log_test")
    log = setup_logging(run_dir, console_level="WARNING")
    log_path = os.path.join(run_dir, "cas.log")
    assert os.path.exists(log_path)


def test_logging_no_duplicate_handlers(tmp_path):
    """Calling setup_logging twice doesn't add duplicate handlers."""
    run_dir = str(tmp_path / "run_dup_log")
    log = setup_logging(run_dir, console_level="WARNING")
    n_handlers = len(log.handlers)
    log2 = setup_logging(run_dir, console_level="WARNING")
    assert len(log2.handlers) == n_handlers, (
        "Duplicate handlers added on second setup_logging call"
    )


# ── CLI argument parsing ──────────────────────────────────────────────────────

def test_parse_args_defaults():
    """Default arguments are set correctly."""
    args = parse_args([])
    assert args.budget     == 1.0
    assert args.report     == "html"
    assert args.log_level  == "INFO"
    assert args.list_systems is False
    assert args.n_sims is None        # defers to simulation.yaml


def test_parse_args_custom_n_sims():
    args = parse_args(["--n-sims", "500"])
    assert args.n_sims == 500


def test_parse_args_custom_budget():
    args = parse_args(["--budget", "5.0"])
    assert args.budget == 5.0


def test_parse_args_report_formats():
    args = parse_args(["--report", "html,pdf,json"])
    # Formats are parsed as a comma-string; splitting happens in main()
    assert "html" in args.report
    assert "pdf"  in args.report


def test_parse_args_list_systems_flag():
    args = parse_args(["--list-systems"])
    assert args.list_systems is True


def test_parse_args_custom_configs(tmp_path):
    """Custom config paths are accepted without error."""
    # Create a minimal valid yaml to point at
    f = tmp_path / "w.yaml"
    import yaml
    f.write_text(yaml.dump({
        "version": "1.0",
        "systems": {
            "X": {
                "unit_cost": 1,
                "tier": "T",
                "type": "t",
                "quality_tier": "LOW",
                "dud_rate": 0.1,
                "consumption_rates": {
                    "theater_1": {"mean": 1, "cv": 0.5},
                    "theater_2": {"mean": 1, "cv": 0.5},
                }
            }
        }
    }))
    args = parse_args(["--weapon-config", str(f)])
    assert args.weapon_config == str(f)


def test_parse_args_log_levels():
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        args = parse_args(["--log-level", level])
        assert args.log_level == level


def test_parse_args_horizon():
    args = parse_args(["--horizon", "60"])
    assert args.horizon == 60


def test_parse_args_run_id_override():
    args = parse_args(["--run-id", "my_custom_run"])
    assert args.run_id == "my_custom_run"


def test_help_flag_exits(capsys):
    """--help exits with code 0 (SystemExit)."""
    with pytest.raises(SystemExit) as exc:
        parse_args(["--help"])
    assert exc.value.code == 0
