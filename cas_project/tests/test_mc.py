"""
tests/test_mc.py
Unit tests for the Monte Carlo simulation engine.
Uses a small n_sims (200) so the test suite runs quickly.
"""
import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cas.config import Config
from cas.mc_simulator import (
    readiness_probability,
    days_coverage_distribution,
    optimise_portfolio,
    run_full_mc,
    _nb_sample,
    _make_rng,
)


@pytest.fixture(scope="module")
def cfg_fast():
    """Low n_sims Config for fast tests."""
    cfg = Config()
    cfg.n_sims = 200
    return cfg


# ── NB sampler ────────────────────────────────────────────────────────────────

def test_nb_sample_positive_mean():
    """NB sampler produces non-negative values with correct mean."""
    rng = _make_rng(42)
    samples = _nb_sample(rng, mu=10.0, cv=0.4, n=5000)
    assert samples.min() >= 0
    assert abs(samples.mean() - 10.0) < 1.0, (
        f"NB mean {samples.mean():.2f} deviates too far from 10.0"
    )


def test_nb_sample_zero_mu():
    """NB sampler returns zeros when mu=0."""
    rng = _make_rng(42)
    samples = _nb_sample(rng, mu=0.0, cv=0.5, n=100)
    assert np.all(samples == 0)


def test_nb_sample_reproducible():
    """Same seed produces identical samples."""
    rng1 = _make_rng(123)
    rng2 = _make_rng(123)
    s1 = _nb_sample(rng1, 5.0, 0.4, 50)
    s2 = _nb_sample(rng2, 5.0, 0.4, 50)
    assert np.array_equal(s1, s2)


def test_nb_sample_overdispersion():
    """NB variance should exceed the mean (overdispersion)."""
    rng = _make_rng(0)
    samples = _nb_sample(rng, mu=20.0, cv=0.5, n=10000)
    assert samples.var() > samples.mean(), "NB should be overdispersed"


# ── Readiness probability ─────────────────────────────────────────────────────

def test_readiness_returns_dict(cfg_fast):
    result = readiness_probability(cfg_fast, "THAAD", horizon_days=90)
    assert isinstance(result, dict)
    assert "P_coverage" in result


def test_readiness_p_in_range(cfg_fast):
    """P_coverage is between 0 and 1."""
    for system in ["THAAD", "PAC3_MSE", "Tomahawk_TLAM"]:
        r = readiness_probability(cfg_fast, system, 90)
        assert 0.0 <= r["P_coverage"] <= 1.0, (
            f"{system}: P_coverage={r['P_coverage']} out of [0,1]"
        )


def test_readiness_thaad_low_coverage(cfg_fast):
    """THAAD should have <80% coverage probability at 90-day two-war."""
    r = readiness_probability(cfg_fast, "THAAD", 90)
    assert r["P_coverage"] < 0.80, (
        f"THAAD P_coverage={r['P_coverage']:.2%}: expected low coverage at day 90"
    )


def test_readiness_surge_improves_coverage(cfg_fast):
    """Production surge should increase P_coverage."""
    base  = readiness_probability(cfg_fast, "PAC3_MSE", 90, 0.0)
    surge = readiness_probability(cfg_fast, "PAC3_MSE", 90, 2.0)
    assert surge["P_coverage"] >= base["P_coverage"], (
        "Surge should not decrease coverage probability"
    )


def test_readiness_unknown_system(cfg_fast):
    """Unknown system key returns empty dict without raising."""
    result = readiness_probability(cfg_fast, "NO_SUCH_SYSTEM", 90)
    assert result == {}


def test_readiness_percentile_ordering(cfg_fast):
    """p5 <= mean <= p95."""
    r = readiness_probability(cfg_fast, "Tomahawk_TLAM", 60)
    assert r["p5_remaining"] <= r["mean_remaining"], (
        "p5_remaining should be <= mean_remaining"
    )
    assert r["mean_remaining"] <= r["p95_remaining"] + 1, (
        "mean_remaining should be <= p95_remaining (with tolerance)"
    )


# ── Days coverage distribution ────────────────────────────────────────────────

def test_coverage_returns_dict(cfg_fast):
    result = days_coverage_distribution(cfg_fast, "THAAD")
    assert "median_days" in result
    assert "p25_days" in result
    assert "p75_days" in result


def test_coverage_extra_units_improves_median(cfg_fast):
    """Adding inventory should increase median days coverage."""
    base = days_coverage_distribution(cfg_fast, "THAAD", extra_units=0)
    aug  = days_coverage_distribution(cfg_fast, "THAAD", extra_units=500)
    assert aug["median_days"] >= base["median_days"], (
        "Extra units should not decrease median days"
    )


def test_coverage_iqr_ordering(cfg_fast):
    """p25 <= median <= p75."""
    r = days_coverage_distribution(cfg_fast, "PAC3_MSE")
    assert r["p25_days"] <= r["median_days"] <= r["p75_days"], (
        f"IQR ordering violated: {r['p25_days']} <= {r['median_days']} <= {r['p75_days']}"
    )


# ── Portfolio optimisation ────────────────────────────────────────────────────

def test_portfolio_returns_dict(cfg_fast):
    result = optimise_portfolio(cfg_fast, budget_B=0.5, horizon_days=60)
    assert "allocation_M"  in result
    assert "final_days"    in result
    assert "unspent_M"     in result
    assert "caps_hit"      in result
    assert "tier_spent_M"  in result


def test_portfolio_allocation_non_negative(cfg_fast):
    """All system allocations are non-negative."""
    result = optimise_portfolio(cfg_fast, 1.0, 60)
    for sys, alloc in result["allocation_M"].items():
        assert alloc >= 0, f"{sys}: negative allocation {alloc}"


def test_portfolio_total_spend_within_budget(cfg_fast):
    """Total allocated + unspent == budget (caps may leave money unspent)."""
    budget_M = 500
    result = optimise_portfolio(cfg_fast, budget_B=0.5, horizon_days=60)
    allocated = sum(result["allocation_M"].values())
    total = allocated + result["unspent_M"]
    assert abs(total - budget_M) < 1, (
        f"Budget accounting error: allocated({allocated:.1f}M) + "
        f"unspent({result['unspent_M']:.1f}M) = {total:.1f}M != {budget_M}M"
    )
    # Allocated <= budget (caps may leave some unspent)
    assert allocated <= budget_M + 0.01, (
        f"Over-allocated: {allocated:.1f}M > budget {budget_M}M"
    )


def test_portfolio_tier_caps_respected(cfg_fast):
    """No tier receives more than its configured cap fraction of total budget."""
    from cas.mc_simulator import _resolve_caps
    budget_B = 1.0
    result = optimise_portfolio(cfg_fast, budget_B=budget_B, horizon_days=60)
    tier_caps_frac, per_sys_frac = _resolve_caps(cfg_fast)
    budget_M = budget_B * 1000
    tier_spent = result.get("tier_spent_M", {})
    for tier, spent_M in tier_spent.items():
        cap_M = tier_caps_frac.get(tier, 1.0) * budget_M
        assert spent_M <= cap_M + 0.01, (
            f"Tier {tier} spent ${spent_M:.0f}M > cap ${cap_M:.0f}M"
        )


def test_portfolio_per_system_cap_respected(cfg_fast):
    """No single system receives more than the per-system cap."""
    from cas.mc_simulator import _resolve_caps
    budget_B = 1.0
    result = optimise_portfolio(cfg_fast, budget_B=budget_B, horizon_days=60)
    _, per_sys_frac = _resolve_caps(cfg_fast)
    per_sys_cap_M = budget_B * 1000 * per_sys_frac
    for sys, alloc_M in result["allocation_M"].items():
        assert alloc_M <= per_sys_cap_M + 0.01, (
            f"{sys}: ${alloc_M:.0f}M > per-system cap ${per_sys_cap_M:.0f}M"
        )


def test_portfolio_zero_budget(cfg_fast):
    """Zero budget produces zero allocations."""
    result = optimise_portfolio(cfg_fast, budget_B=0.0, horizon_days=60)
    total = sum(result["allocation_M"].values())
    assert total == 0.0


# ── run_full_mc ───────────────────────────────────────────────────────────────

def test_portfolio_infantry_cap_respected(cfg_fast):
    """INFANTRY_CUAS systems must not exceed 10% of budget."""
    budget_B = 1.0
    result = optimise_portfolio(cfg_fast, budget_B=budget_B, horizon_days=60)
    budget_M = budget_B * 1000
    infantry_max_M = budget_M * 0.10
    infantry_systems = [
        s for s, ws in cfg_fast.weapons.items()
        if ws.get("tier") == "INFANTRY_CUAS"
    ]
    infantry_total = sum(
        result["allocation_M"].get(s, 0) for s in infantry_systems
    )
    assert infantry_total <= infantry_max_M + 1, (
        f"INFANTRY_CUAS allocation ${infantry_total:.0f}M exceeds "
        f"10% cap ${infantry_max_M:.0f}M"
    )


def test_portfolio_per_system_cap_respected(cfg_fast):
    """No single system may exceed 25% of total budget."""
    budget_B = 1.0
    result = optimise_portfolio(cfg_fast, budget_B=budget_B, horizon_days=60)
    per_sys_max_M = budget_B * 1000 * 0.25
    for sys, alloc in result["allocation_M"].items():
        assert alloc <= per_sys_max_M + 1, (
            f"{sys}: allocation ${alloc:.0f}M exceeds "
            f"25% per-system cap ${per_sys_max_M:.0f}M"
        )


def test_portfolio_caps_hit_is_list(cfg_fast):
    """caps_hit is a list (may be empty if budget too small to trigger caps)."""
    result = optimise_portfolio(cfg_fast, budget_B=0.1, horizon_days=60)
    assert isinstance(result["caps_hit"], list)


def test_run_full_mc_structure(cfg_fast):
    """run_full_mc returns dict with 'readiness' and 'coverage' keys."""
    result = run_full_mc(cfg_fast, horizon=30)
    assert "readiness" in result
    assert "coverage" in result
    assert len(result["readiness"]) > 0
    assert len(result["coverage"]) > 0


def test_run_full_mc_system_keys_match(cfg_fast):
    """readiness and coverage dicts have the same system keys."""
    result = run_full_mc(cfg_fast, 30)
    assert set(result["readiness"].keys()) == set(result["coverage"].keys())
