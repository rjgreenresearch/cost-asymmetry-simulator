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

# ── Allocation caps by tier — prevents unrealistic concentration ─────────────
# No responsible defence planner would allocate 90% of a $1B budget to
# shotgun shells. These caps enforce portfolio diversification by tier
# Cap defaults — used when simulation.yaml does not define portfolio_caps.
# These are overridden by config/simulation.yaml → targets.portfolio_caps.
# To disable a cap for a tier, set its value to 1.0 in simulation.yaml.
_DEFAULT_TIER_CAPS: dict[str, float] = {
    "STRATEGIC":           0.50,   # THAAD, SM-3: max 50%
    "OPERATIONAL":         0.40,   # PAC-3, SM-2, SM-6: max 40%
    "PRECISION_STRIKE":    0.30,   # Tomahawk, JASSM-ER: max 30%
    "ATTRITION_OFFENSE":   0.25,   # LUCAS, FPV, Switchblade: max 25%
    "ATTRITION_DEFENSE":   0.20,   # DroneHunter: max 20%
    "INFANTRY_CUAS":       0.20,   # Skynet, DroneRound: max 20%
    "STRUCTURAL_SOLUTION": 1.00,   # DEW: no cap (always highest priority)
}
_DEFAULT_PER_SYSTEM_CAP = 0.30    # no single system > 30% of total budget


def _resolve_caps(cfg: Config) -> tuple[dict[str, float], float]:
    """
    Load tier caps from simulation.yaml (targets.portfolio_caps) if present,
    falling back to _DEFAULT_TIER_CAPS. Returns (tier_cap_dict, per_system_cap).
    Both are expressed as fractions of total budget (0.0 – 1.0).
    """
    yaml_caps = cfg.portfolio_caps  # populated from simulation.yaml
    tier_caps = {}
    for tier, default in _DEFAULT_TIER_CAPS.items():
        tier_caps[tier] = float(yaml_caps.get(tier, default))
    per_sys = float(yaml_caps.get("_per_system", _DEFAULT_PER_SYSTEM_CAP))
    return tier_caps, per_sys


def optimise_portfolio(
    cfg: Config,
    budget_B: float = 1.0,
    horizon_days: int = 90,
    systems: list[str] | None = None,
) -> dict:
    """
    Allocate `budget_B` billion dollars across `systems` to maximise the
    minimum median days-of-coverage using a greedy marginal-value algorithm
    subject to tier-level and per-system allocation caps.

    Caps prevent unrealistic concentration (e.g. 90% of budget into shotgun
    shells) while preserving the greedy marginal-value logic. Caps reflect
    real defence procurement constraints: strategic interceptors are capacity-
    limited; infantry munitions are last-resort, not primary investment.

    Tier caps (_TIER_CAP_PCT):
      STRATEGIC          40% — THAAD, SM-3: scarcity limits absorption
      OPERATIONAL        30% — PAC-3, SM-2, SM-6
      PRECISION_STRIKE   25% — Tomahawk, JASSM-ER
      ATTRITION_OFFENSE  20% — LUCAS, FPV drones
      STRUCTURAL_SOLUTION 20% — DEW systems
      ATTRITION_DEFENSE  15% — DroneHunter
      INFANTRY_CUAS      10% — Skynet shells, Drone Rounds

    Per-system cap: no single system > 25% of total budget.

    Parameters
    ----------
    systems : list of system keys, or None (all consumable systems)

    Returns
    -------
    dict with allocation_M, final_median_days, rationale, caps_applied
    """
    if systems is None:
        systems = list(cfg.consumable_systems().keys())

    step_M    = cfg.targets.get("budget_step_M", 100)
    budget_M  = budget_B * 1000
    remaining = budget_M

    # Resolve caps from config (YAML overrides defaults)
    tier_caps_frac, per_sys_frac = _resolve_caps(cfg)
    tier_cap_M:   dict[str, float] = {t: budget_M * f
                                       for t, f in tier_caps_frac.items()}
    per_sys_cap_M = budget_M * per_sys_frac
    log.debug("Resolved tier caps: %s",
              {t: f"${v:.0f}M ({tier_caps_frac[t]:.0%})"
               for t, v in tier_cap_M.items()})
    log.debug("Per-system cap: $%.0fM (%.0f%%)", per_sys_cap_M, per_sys_frac*100)

    # Track allocation per system and per tier
    augments   = {s: 0 for s in systems}
    allocation = {s: 0.0 for s in systems}
    tier_spent: dict[str, float] = {}
    rationale  = {s: [] for s in systems}
    caps_hit   = []

    def _tier(s: str) -> str:
        return cfg.weapons[s].get("tier", "OPERATIONAL")

    def _baseline(s: str) -> float:
        r = days_coverage_distribution(cfg, s, extra_units=augments[s])
        return r.get("median_days", 0.0)

    def _at_cap(s: str) -> bool:
        """True if this system or its tier has hit its allocation cap."""
        if allocation[s] + step_M > per_sys_cap_M:
            return True
        t = _tier(s)
        if t in tier_cap_M:
            spent = tier_spent.get(t, 0.0)
            if spent + step_M > tier_cap_M[t]:
                return True
        return False

    log.info(
        "Portfolio optimisation: budget=$%.0fB  step=$%dM  "
        "per_sys_cap=$%.0fM  systems=%s",
        budget_B, step_M, per_sys_cap_M, systems,
    )
    log.debug("Tier caps: %s", {k: f"${v:.0f}M" for k, v in tier_cap_M.items()})

    rounds = 0
    max_rounds = cfg.targets.get("max_optimiser_rounds", 100)

    while remaining >= step_M and rounds < max_rounds:
        best_sys  = None
        best_gain = -1.0

        for sys in systems:
            if _at_cap(sys):
                continue                     # skip capped systems

            ws        = cfg.weapons[sys]
            unit_cost = ws.get("unit_cost", ws.get("unit_cost_per_shot", 1))
            if unit_cost <= 0:
                continue
            units = int(step_M * 1e6 / unit_cost)
            if units == 0:
                continue

            base = _baseline(sys)
            augments[sys] += units
            augmented = _baseline(sys)
            augments[sys] -= units

            gain = augmented - base
            if gain > best_gain:
                best_gain  = gain
                best_sys   = sys
                best_units = units

        if best_sys is None or best_gain <= 0:
            log.info("Optimiser converged at round %d (no uncapped gains)", rounds)
            break

        # Apply allocation
        augments[best_sys]   += best_units
        allocation[best_sys] += step_M
        tier = _tier(best_sys)
        tier_spent[tier]      = tier_spent.get(tier, 0.0) + step_M
        remaining            -= step_M
        new_median            = _baseline(best_sys)

        # Check if cap newly triggered
        if _at_cap(best_sys):
            cap_msg = (
                f"{best_sys} reached per-system cap "
                f"(${allocation[best_sys]:.0f}M / ${per_sys_cap_M:.0f}M)"
                if allocation[best_sys] >= per_sys_cap_M
                else f"{tier} tier reached cap "
                     f"(${tier_spent[tier]:.0f}M / ${tier_cap_M.get(tier,0):.0f}M)"
            )
            caps_hit.append(cap_msg)
            log.info("Cap reached: %s", cap_msg)

        rationale[best_sys].append(
            f"+${step_M}M → +{best_units:,} units → median {new_median:.0f} days"
        )
        log.debug(
            "Round %d: $%dM → %s (+%d units, +%.1f days) "
            "[tier %s: $%.0fM spent]",
            rounds, step_M, best_sys, best_units, best_gain,
            tier, tier_spent.get(tier, 0),
        )
        rounds += 1

    final_days = {s: round(_baseline(s), 1) for s in systems}

    log.info(
        "Portfolio complete: %d rounds, $%.0fM allocated, $%.0fM unspent, "
        "%d caps triggered",
        rounds, budget_M - remaining, remaining, len(caps_hit),
    )

    return {
        "budget_B":       budget_B,
        "step_M":         step_M,
        "rounds":         rounds,
        "allocation_M":   allocation,
        "tier_spent_M":   tier_spent,
        "final_days":     final_days,
        "rationale":      rationale,
        "caps_hit":       caps_hit,
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
