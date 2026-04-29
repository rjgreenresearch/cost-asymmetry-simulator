"""
cas/mc_simulator.py
Monte Carlo inventory optimisation engine.
Adapted from the Dyna-METRIC readiness-based sparing framework
(Sherbrooke 1968; RAND R-1872-AF) for consumable munitions.

Three modules:
  1. readiness_probability  — P(not-stockout) at day D across N simulations
  2. days_coverage_dist     — distribution of days-to-zero (key output metric)
  3. optimise_portfolio     — greedy marginal-value portfolio allocation
"""

import logging
import numpy as np
from .config import Config

log = logging.getLogger("cas.mc")


def _make_rng(seed) -> np.random.Generator:
    return np.random.default_rng(seed if seed is not None else None)


def _nb_sample(rng: np.random.Generator, mu: float, cv: float, n: int) -> np.ndarray:
    """
    Sample n values from a Negative Binomial distribution with mean=mu, CV=cv.
    NB is preferred over Poisson for munitions demand because it accommodates
    overdispersion — combat demand is 'bursty' relative to a Poisson process.
    Falls back gracefully when mu ≤ 0.
    """
    if mu <= 0:
        return np.zeros(n, dtype=float)
    std = mu * cv
    var = std ** 2
    if var <= mu:
        var = mu * 1.01          # enforce overdispersion
    p = min(0.9999, mu / var)
    r = max(0.0001, mu ** 2 / (var - mu))
    return rng.negative_binomial(r, p, size=n).astype(float)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — Readiness Probability
# ─────────────────────────────────────────────────────────────────────────────

def readiness_probability(
    cfg: Config,
    system_key: str,
    horizon_days: int = 90,
    production_surge_pct: float = 0.0,
) -> dict:
    """
    Estimate P(inventory > 0) at day `horizon_days` under two-war stochastic demand.

    Parameters
    ----------
    cfg : Config
    system_key : str — must be a consumable system in cfg.weapons
    horizon_days : int — simulation horizon
    production_surge_pct : float — fractional increase above baseline production

    Returns
    -------
    dict with P_coverage, mean_remaining, percentile bands, and metadata
    """
    ws = cfg.weapons.get(system_key)
    if not ws:
        log.warning("readiness_probability: unknown system '%s'", system_key)
        return {}

    cr     = ws.get("consumption_rates", {})
    t1     = cr.get("theater_1", {})
    t2     = cr.get("theater_2", {})
    mu1, cv1 = t1.get("mean", 0), t1.get("cv", 0.5)
    mu2, cv2 = t2.get("mean", 0), t2.get("cv", 0.5)

    corr   = ws.get("theater_correlation", cfg.theater_correlation)
    inv0   = ws.get("inventory_est", 0)
    annual = ws.get("annual_production", ws.get("annual_production_target", 0))
    d_prod = (annual / 365.0) * (1 + production_surge_pct)

    n      = cfg.n_sims
    rng    = _make_rng(cfg.random_seed)

    stockouts = 0
    remaining = []

    log.debug("readiness_probability(%s): n=%d horizon=%d inv=%d d_prod=%.1f",
              system_key, n, horizon_days, inv0, d_prod)

    for _ in range(n):
        inv = float(inv0)
        for _ in range(horizon_days):
            d1 = float(_nb_sample(rng, mu1, cv1, 1)[0])
            # Theater correlation: T2 demand shifts proportionally with T1 burst
            mu2_adj = mu2 * (1 + corr * (d1 / mu1 - 1)) if mu1 > 0 else mu2
            d2 = float(_nb_sample(rng, max(0, mu2_adj), cv2, 1)[0])
            inv = max(0.0, inv - (d1 + d2) + d_prod)
            if inv == 0.0:
                stockouts += 1
                break
        remaining.append(inv)

    arr = np.array(remaining)
    result = {
        "system":          system_key,
        "horizon_days":    horizon_days,
        "n_simulations":   n,
        "inventory_start": inv0,
        "quality_tier":    ws.get("quality_tier", "—"),
        "dud_rate_pct":    round(ws.get("dud_rate", 0) * 100, 1),
        "P_coverage":      round(1 - stockouts / n, 4),
        "mean_remaining":  round(float(arr.mean()), 1),
        "p5_remaining":    round(float(np.percentile(arr, 5)), 1),
        "p25_remaining":   round(float(np.percentile(arr, 25)), 1),
        "p75_remaining":   round(float(np.percentile(arr, 75)), 1),
        "p95_remaining":   round(float(np.percentile(arr, 95)), 1),
    }
    log.info("readiness(%s @ d%d): P=%.2f%%  mean_rem=%.0f",
             system_key, horizon_days,
             result["P_coverage"] * 100, result["mean_remaining"])
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — Days-of-Coverage Distribution
# ─────────────────────────────────────────────────────────────────────────────

def days_coverage_distribution(
    cfg: Config,
    system_key: str,
    extra_units: int = 0,
    max_days: int = 365,
) -> dict:
    """
    Run N simulations and record the number of days until inventory hits zero.
    Returns median, IQR, and full percentile profile.

    Parameters
    ----------
    extra_units : int — augment the starting inventory (for marginal analysis)
    max_days    : int — cap on simulation length (default 365)
    """
    ws = cfg.weapons.get(system_key)
    if not ws:
        return {}

    cr     = ws.get("consumption_rates", {})
    t1     = cr.get("theater_1", {})
    t2     = cr.get("theater_2", {})
    mu1, cv1 = t1.get("mean", 0), t1.get("cv", 0.5)
    mu2, cv2 = t2.get("mean", 0), t2.get("cv", 0.5)

    corr   = ws.get("theater_correlation", cfg.theater_correlation)
    inv0   = ws.get("inventory_est", 0) + extra_units
    annual = ws.get("annual_production", ws.get("annual_production_target", 0))
    d_prod = annual / 365.0

    n   = cfg.n_sims
    rng = _make_rng(cfg.random_seed)
    survived = []

    for _ in range(n):
        inv = float(inv0)
        day = 0
        while inv > 0 and day < max_days:
            d1 = float(_nb_sample(rng, mu1, cv1, 1)[0])
            mu2_adj = mu2 * (1 + corr * (d1 / mu1 - 1)) if mu1 > 0 else mu2
            d2 = float(_nb_sample(rng, max(0, mu2_adj), cv2, 1)[0])
            inv = max(0.0, inv - (d1 + d2) + d_prod)
            day += 1
        survived.append(day)

    arr = np.array(survived)
    return {
        "system":        system_key,
        "extra_units":   extra_units,
        "inventory_used": inv0,
        "n_simulations": n,
        "median_days":   round(float(np.median(arr)), 1),
        "mean_days":     round(float(arr.mean()), 1),
        "p10_days":      round(float(np.percentile(arr, 10)), 1),
        "p25_days":      round(float(np.percentile(arr, 25)), 1),
        "p75_days":      round(float(np.percentile(arr, 75)), 1),
        "p90_days":      round(float(np.percentile(arr, 90)), 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — Portfolio Optimisation
# Greedy marginal-value algorithm: allocates a fixed budget to maximise
# minimum days-of-coverage across the critical interceptor portfolio.
# ─────────────────────────────────────────────────────────────────────────────

def optimise_portfolio(
    cfg: Config,
    budget_B: float = 1.0,
    horizon_days: int = 90,
    systems: list[str] | None = None,
) -> dict:
    """
    Allocate `budget_B` billion dollars across `systems` to maximise the
    minimum median days-of-coverage using a greedy marginal-value algorithm.

    The greedy algorithm is not guaranteed globally optimal but is:
      (a) tractable for real-time computation
      (b) interpretable for academic and policy audiences
      (c) consistent with the Dyna-METRIC approach to readiness sparing

    Parameters
    ----------
    systems : list of system keys to consider, or None (uses all consumables)

    Returns
    -------
    dict with allocation_M, final_median_days, rationale per system
    """
    if systems is None:
        systems = [k for k in cfg.consumable_systems()
                   if cfg.weapons[k].get("type") not in
                   ("one_way_attack_drone", "fpv_attack_drone",
                    "c_uas_interceptor_drone")]  # focus on interceptors

    step_M    = cfg.targets.get("budget_step_M", 100)
    budget_M  = budget_B * 1000
    remaining = budget_M

    # Working inventory augments per system
    augments  = {s: 0 for s in systems}
    allocation = {s: 0.0 for s in systems}
    rationale  = {s: [] for s in systems}

    def _baseline(s):
        r = days_coverage_distribution(cfg, s, extra_units=augments[s])
        return r.get("median_days", 0)

    log.info("Portfolio optimisation: budget=$%.0fB  step=$%dM  systems=%s",
             budget_B, step_M, systems)

    rounds = 0
    max_rounds = cfg.targets.get("max_optimiser_rounds", 100)

    while remaining >= step_M and rounds < max_rounds:
        best_sys  = None
        best_gain = -1.0

        for sys in systems:
            ws        = cfg.weapons[sys]
            unit_cost = ws.get("unit_cost", ws.get("unit_cost_per_shot", 1))
            if unit_cost <= 0:
                continue
            units = int(step_M * 1e6 / unit_cost)
            if units == 0:
                continue

            base   = _baseline(sys)
            augments[sys] += units
            augmented = _baseline(sys)
            augments[sys] -= units

            gain = augmented - base
            if gain > best_gain:
                best_gain = gain
                best_sys  = sys
                best_units = units

        if best_sys is None or best_gain <= 0:
            log.info("Optimiser converged at round %d; no further gains", rounds)
            break

        augments[best_sys]   += best_units
        allocation[best_sys] += step_M
        remaining            -= step_M
        new_median            = _baseline(best_sys)
        rationale[best_sys].append(
            f"+${step_M}M → +{best_units} units → median {new_median:.0f} days"
        )
        log.debug("Round %d: allocate $%dM to %s (+%d units, gain=%.1f days)",
                  rounds, step_M, best_sys, best_units, best_gain)
        rounds += 1

    # Final coverage profile
    final_days = {s: round(_baseline(s), 1) for s in systems}

    return {
        "budget_B":       budget_B,
        "step_M":         step_M,
        "rounds":         rounds,
        "allocation_M":   allocation,
        "final_days":     final_days,
        "rationale":      rationale,
        "unspent_M":      remaining,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: run all three modules for all consumable systems
# ─────────────────────────────────────────────────────────────────────────────

def run_full_mc(cfg: Config, horizon: int = 90) -> dict:
    """
    Run readiness + coverage distribution for every consumable system.
    Returns a structured dict suitable for JSON export and reporting.
    """
    log.info("Running full MC analysis: horizon=%d days  n=%d", horizon, cfg.n_sims)
    readiness, coverage = {}, {}

    for key in cfg.consumable_systems():
        readiness[key] = readiness_probability(cfg, key, horizon)
        coverage[key]  = days_coverage_distribution(cfg, key)

    return {"readiness": readiness, "coverage": coverage}
