"""
tests/test_config.py
Unit tests for the Config loader.
"""
import os
import sys
import pytest
import yaml
import tempfile

# Ensure the cas package is importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cas.config import Config, _load_yaml, load_weapon_systems


# ── _load_yaml ────────────────────────────────────────────────────────────────

def test_load_yaml_missing_file():
    """FileNotFoundError with helpful hint when file does not exist."""
    with pytest.raises(FileNotFoundError, match="Tip:"):
        _load_yaml("/nonexistent/path/config.yaml")


def test_load_yaml_invalid_yaml(tmp_path):
    """ValueError when file contains invalid YAML."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("key: [\nbad yaml\n")
    with pytest.raises(ValueError, match="YAML parse error"):
        _load_yaml(str(bad))


def test_load_yaml_empty_file(tmp_path):
    """ValueError when file is empty."""
    empty = tmp_path / "empty.yaml"
    empty.write_text("")
    with pytest.raises(ValueError, match="empty"):
        _load_yaml(str(empty))


def test_load_yaml_valid(tmp_path):
    """Valid YAML file loads correctly."""
    f = tmp_path / "good.yaml"
    f.write_text("systems:\n  THAAD:\n    unit_cost: 12700000\n")
    result = _load_yaml(str(f))
    assert result["systems"]["THAAD"]["unit_cost"] == 12_700_000


# ── Config defaults ───────────────────────────────────────────────────────────

def test_config_loads_defaults():
    """Config loads all three YAML files with default paths."""
    cfg = Config()
    assert len(cfg.weapons) > 0
    assert len(cfg.threats) > 0
    assert cfg.n_sims > 0
    assert cfg.theater_correlation > 0


def test_config_weapon_count():
    """Weapon systems database has expected minimum count."""
    cfg = Config()
    assert len(cfg.weapons) >= 13, (
        f"Expected >= 13 weapon systems, got {len(cfg.weapons)}"
    )


def test_config_threat_count():
    """Threat systems database has expected minimum count."""
    cfg = Config()
    assert len(cfg.threats) >= 4, (
        f"Expected >= 4 threat systems, got {len(cfg.threats)}"
    )


def test_config_weapon_accessor_valid():
    """Config.weapon() returns correct data for a known system."""
    cfg = Config()
    thaad = cfg.weapon("THAAD")
    assert thaad["unit_cost"] == 12_700_000
    assert thaad["quality_tier"] == "HIGH"


def test_config_weapon_accessor_invalid():
    """Config.weapon() raises KeyError with helpful message for unknown key."""
    cfg = Config()
    with pytest.raises(KeyError, match="Unknown weapon system"):
        cfg.weapon("DOES_NOT_EXIST")


def test_config_consumable_systems():
    """consumable_systems() returns only systems with consumption_rates."""
    cfg = Config()
    consumable = cfg.consumable_systems()
    assert len(consumable) > 0
    for key, ws in consumable.items():
        assert "consumption_rates" in ws, f"{key} missing consumption_rates"
        assert ws["consumption_rates"]["theater_1"]["mean"] > 0


def test_config_horizon_names():
    """Named horizons return sensible integer day counts."""
    cfg = Config()
    assert cfg.horizon("short")    == 30
    assert cfg.horizon("medium")   == 60
    assert cfg.horizon("long")     == 90
    assert cfg.horizon("extended") == 180


def test_config_custom_weapon_file(tmp_path):
    """Config accepts a custom weapon_systems.yaml path."""
    custom = tmp_path / "custom_weapons.yaml"
    custom.write_text(yaml.dump({
        "version": "1.0",
        "systems": {
            "TEST_SYSTEM": {
                "unit_cost": 999,
                "tier": "TEST",
                "type": "test",
                "quality_tier": "MED",
                "dud_rate": 0.05,
                "consumption_rates": {
                    "theater_1": {"mean": 1, "cv": 0.5},
                    "theater_2": {"mean": 1, "cv": 0.5},
                }
            }
        }
    }))
    cfg = Config(weapon_systems_path=str(custom))
    assert "TEST_SYSTEM" in cfg.weapons
    assert cfg.weapon("TEST_SYSTEM")["unit_cost"] == 999
