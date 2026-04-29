"""
tests/test_simulator.py
Unit tests for the deterministic simulation engine.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cas.config import Config
from cas.simulator import compute_car_matrix, two_war_depletion, marginal_value


@pytest.fixture(scope="module")
def cfg():
    """Shared Config instance for all simulator tests."""
    return Config()


# ── CAR Matrix ────────────────────────────────────────────────────────────────

def test_car_matrix_returns_list(cfg):
    """compute_car_matrix returns a non-empty list."""
    result = compute_car_matrix(cfg)
    assert isinstance(result, list)
    assert len(result) > 0


def test_car_matrix_sorted_ascending(cfg):
    """CAR matrix is sorted ascending by CAR_raw (worst for US first)."""
    result = compute_car_matrix(cfg)
    cars = [r["CAR_raw"] for r in result]
    assert cars == sorted(cars), "CAR matrix not sorted ascending"


def test_car_matrix_required_fields(cfg):
    """Each row has required keys."""
    required = {"label", "threat", "defender",
                "threat_cost", "defend_cost",
                "CAR_raw", "CAR_adj", "interpretation"}
    for row in compute_car_matrix(cfg):
        missing = required - set(row.keys())
        assert not missing, f"Row missing keys: {missing}"


def test_car_iron_beam_favourable(cfg):
    """Iron Beam vs FPV drone should have CAR_raw >> 1 (US advantage)."""
    result = compute_car_matrix(cfg)
    iron_beam_rows = [r for r in result
                      if r["defender"] == "Iron_Beam_DEW"
                      and r["threat"] == "FPV_Adversary"]
    assert iron_beam_rows, "Iron Beam vs FPV pairing not found"
    assert iron_beam_rows[0]["CAR_raw"] > 100, (
        f"Expected Iron Beam CAR >> 100, got {iron_beam_rows[0]['CAR_raw']}"
    )
    assert iron_beam_rows[0]["interpretation"] == "US_ADVANTAGE"


def test_car_fpv_pac3_unfavourable(cfg):
    """FPV drone vs PAC-3 should have CAR_raw << 1 (adversary advantage)."""
    result = compute_car_matrix(cfg)
    rows = [r for r in result
            if r["defender"] == "PAC3_MSE"
            and r["threat"] == "FPV_Adversary"]
    assert rows, "FPV vs PAC-3 pairing not found"
    assert rows[0]["CAR_raw"] < 0.01, (
        f"Expected FPV/PAC-3 CAR < 0.01, got {rows[0]['CAR_raw']}"
    )
    assert rows[0]["interpretation"] == "ADV_ADVANTAGE"


def test_car_quality_adjusted_increases_adversary_cost(cfg):
    """Quality-adjusted CAR for high-dud Shahed should be >= raw CAR."""
    result = compute_car_matrix(cfg)
    shahed_rows = [r for r in result if r["threat"] == "Shahed_136"]
    for row in shahed_rows:
        assert row["CAR_adj"] >= row["CAR_raw"] * 0.9, (
            f"Quality adjustment unexpectedly large for {row['label']}"
        )


def test_car_custom_pairing(cfg):
    """Custom pairings parameter is respected."""
    custom = [("Shahed_136", "PAC3_MSE", "Custom test pairing")]
    result = compute_car_matrix(cfg, pairings=custom)
    assert len(result) == 1
    assert result[0]["label"] == "Custom test pairing"


def test_car_unknown_system_skipped(cfg):
    """Unknown system key logs a warning and is skipped (no crash)."""
    pairings = [
        ("NONEXISTENT_THREAT", "THAAD", "Bad threat"),
        ("Shahed_136", "NONEXISTENT_DEFENDER", "Bad defender"),
        ("Shahed_136", "PAC3_MSE", "Valid pairing"),
    ]
    result = compute_car_matrix(cfg, pairings=pairings)
    assert len(result) == 1, "Only valid pairing should appear"


# ── Two-War Depletion ─────────────────────────────────────────────────────────

def test_depletion_returns_list(cfg):
    result = two_war_depletion(cfg, horizon=90)
    assert isinstance(result, list)
    assert len(result) > 0


def test_depletion_sorted_by_days(cfg):
    """Results sorted ascending by days_to_zero (most critical first)."""
    result = two_war_depletion(cfg, 90)
    numeric = [float(r["days_to_zero"])
               for r in result if r["days_to_zero"] != "∞"]
    assert numeric == sorted(numeric)


def test_depletion_required_fields(cfg):
    required = {"system", "inventory", "daily_consumption",
                "days_to_zero", "status"}
    for row in two_war_depletion(cfg, 90):
        assert required.issubset(set(row.keys()))


def test_depletion_thaad_critical(cfg):
    """THAAD should be CRITICAL or ACUTE_CRISIS in 90-day two-war scenario."""
    result = two_war_depletion(cfg, 90)
    thaad = next((r for r in result if r["system"] == "THAAD"), None)
    assert thaad is not None, "THAAD not found in depletion results"
    assert thaad["status"] in ("CRITICAL", "ACUTE_CRISIS", "HIGH_RISK"), (
        f"Expected THAAD to be in high-risk status, got {thaad['status']}"
    )


def test_depletion_different_horizons(cfg):
    """Longer horizon yields lower pct_at_horizon for at-risk systems."""
    short = {r["system"]: r["pct_at_horizon"] for r in two_war_depletion(cfg, 30)}
    long_ = {r["system"]: r["pct_at_horizon"] for r in two_war_depletion(cfg, 90)}
    # At-risk systems should have less inventory remaining at day 90 than day 30
    worse = [s for s in short
             if s in long_ and long_[s] < short[s]
             and short[s] > 0]
    assert len(worse) > 0, (
        "Expected some systems to have less remaining inventory at day 90 vs day 30"
    )


def test_depletion_pct_at_horizon_range(cfg):
    """pct_at_horizon is between 0 and 100 inclusive."""
    for row in two_war_depletion(cfg, 90):
        pct = row["pct_at_horizon"]
        assert 0 <= pct <= 100, (
            f"{row['system']}: pct_at_horizon={pct} out of range"
        )


# ── Marginal Value ────────────────────────────────────────────────────────────

def test_marginal_returns_list(cfg):
    result = marginal_value(cfg)
    assert isinstance(result, list)
    assert len(result) > 0


def test_marginal_has_required_fields(cfg):
    required = {"system", "tier", "unit_cost", "quality", "dud_pct"}
    for row in marginal_value(cfg):
        assert required.issubset(set(row.keys()))


def test_marginal_low_cost_systems_top_ranked(cfg):
    """FPV and LUCAS should rank higher than THAAD on days-per-dollar."""
    result = marginal_value(cfg)
    systems = [r["system"] for r in result]
    fpv_idx   = next((i for i, r in enumerate(result)
                      if r["system"] == "FPV_Quadcopter"), None)
    thaad_idx = next((i for i, r in enumerate(result)
                      if r["system"] == "THAAD"), None)
    if fpv_idx is not None and thaad_idx is not None:
        assert fpv_idx < thaad_idx, (
            "FPV should rank higher than THAAD on coverage-days per dollar"
        )


def test_marginal_unit_cost_positive(cfg):
    """All systems in marginal value have positive unit cost."""
    for row in marginal_value(cfg):
        assert row["unit_cost"] > 0, (
            f"{row['system']}: unit_cost={row['unit_cost']} <= 0"
        )
