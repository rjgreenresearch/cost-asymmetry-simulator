"""
cas/simulator.py
Deterministic simulation engine: CAR matrix, two-war depletion,
and marginal-value analysis. All data loaded from Config.
"""

import logging
import math
from .config import Config

log = logging.getLogger("cas.simulator")


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — Cost Asymmetry Ratio Matrix
# CAR = Cost of adversary offensive action / Cost of US defensive response
# CAR > 1 → US cost advantage    CAR < 1 → Adversary cost advantage
# ─────────────────────────────────────────────────────────────────────────────

# Canonical threat / defender pairings
_DEFAULT_PAIRINGS = [
    ("FPV_Adversary",                "PAC3_MSE",      "FPV drone vs Patriot"),
    ("FPV_Adversary",                "THAAD",          "FPV drone vs THAAD"),
    ("FPV_Adversary",                "DroneHunter",    "FPV drone vs drone-hunter"),
    ("FPV_Adversary",                "Iron_Beam_DEW",  "FPV drone vs Iron Beam"),
    ("Shahed_136",                   "PAC3_MSE",       "Shahed vs Patriot"),
    ("Shahed_136",                   "SM2",            "Shahed vs SM-2"),
    ("Shahed_136",                   "DroneHunter",    "Shahed vs drone-hunter"),
    ("Shahed_136",                   "Iron_Beam_DEW",  "Shahed vs Iron Beam"),
    ("Shahed_136",                   "LUCAS",          "Shahed vs LUCAS (mirror)"),
    ("Iranian_Ballistic_Missile_MRBM", "THAAD",        "MRBM vs THAAD"),
    ("Iranian_Ballistic_Missile_MRBM", "SM3_IIA",      "MRBM vs SM-3 IIA"),
    ("Iranian_Ballistic_Missile_MRBM", "PAC3_MSE",     "MRBM vs PAC-3 MSE"),
    ("Hypersonic_Glide_China",       "THAAD",          "DF-17 vs THAAD (no intercept)"),
    ("Chinese_Anti_Ship_Missile_ASBM","SM6",           "ASBM vs SM-6"),
]


def compute_car_matrix(cfg: Config, pairings: list | None = None) -> list[dict]:
    """
    Compute raw and quality-adjusted CAR for every threat/defender pairing.

    Parameters
    ----------
    cfg : Config
    pairings : list of (threat_key, defender_key, label) or None (uses defaults)

    Returns
    -------
    list[dict] sorted ascending by CAR_raw (worst for US first)
    """
    pairings = pairings or _DEFAULT_PAIRINGS
    results = []

    for threat_key, defender_key, label in pairings:
        try:
            threat   = cfg.threat(threat_key)
            defender = cfg.weapon(defender_key)
        except KeyError as exc:
            log.warning("Skipping pairing '%s': %s", label, exc)
            continue

        t_cost_raw = threat["unit_cost"]
        t_dud      = threat.get("dud_rate", 0.05)

        # Directed-energy: use per-shot cost
        d_cost_raw = defender.get("unit_cost_per_shot",
                     defender.get("unit_cost", 0))
        d_dud      = defender.get("dud_rate", 0.03)

        # Hypersonic: currently no effective intercept
        if not threat.get("intercept_possible", True):
            car_raw = car_adj = 0.0
        elif d_cost_raw <= 0:
            car_raw = car_adj = float("inf")
        else:
            car_raw = t_cost_raw / d_cost_raw
            # Quality-adjusted: effective cost = raw / (1 - dud_rate)
            t_eff   = t_cost_raw / max(0.001, 1 - t_dud)
            d_eff   = d_cost_raw / max(0.001, 1 - d_dud)
            car_adj = t_eff / d_eff

        interpretation = (
            "US_ADVANTAGE" if car_raw > 1.0
            else "PARITY"  if 0.8 <= car_raw <= 1.0
            else "ADV_ADVANTAGE"
        )

        results.append({
            "label":         label,
            "threat":        threat_key,
            "defender":      defender_key,
            "threat_cost":   t_cost_raw,
            "threat_dud_pct": round(t_dud * 100, 1),
            "defend_cost":   d_cost_raw,
            "defend_dud_pct": round(d_dud * 100, 1),
            "CAR_raw":       round(car_raw, 4),
            "CAR_adj":       round(car_adj, 4),
            "interpretation": interpretation,
        })
        log.debug("CAR %s: raw=%.4f  adj=%.4f  [%s]",
                  label, car_raw, car_adj, interpretation)

    results.sort(key=lambda r: r["CAR_raw"])
    log.info("CAR matrix: %d pairings computed", len(results))
    return results


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — Deterministic Two-War Depletion
# Linear net-draw model: days-to-zero under mean consumption rates
# Used as complement to MC for quick screening
# ─────────────────────────────────────────────────────────────────────────────

def two_war_depletion(cfg: Config, horizon: int = 90) -> list[dict]:
    """
    For each consumable system compute:
      - Net daily draw = theater_1 + theater_2 - daily_production
      - Days to zero inventory
      - Inventory remaining at `horizon`
      - Required annual production surge to sustain `horizon` days

    Returns list sorted ascending by days_to_zero.
    """
    results = []
    for key, ws in cfg.consumable_systems().items():
        cr      = ws["consumption_rates"]
        c1      = cr["theater_1"]["mean"]
        c2      = cr["theater_2"]["mean"]
        daily   = c1 + c2
        inv     = ws.get("inventory_est", 0)
        annual  = ws.get("annual_production",
                  ws.get("annual_production_target", 0))
        d_prod  = annual / 365.0
        net     = daily - d_prod

        if net <= 0:
            days_to_zero = math.inf
            status = "SELF_SUSTAINING"
        else:
            days_to_zero = inv / net
            if   days_to_zero >= 365: status = "LOW_RISK"
            elif days_to_zero >= 180: status = "MEDIUM_RISK"
            elif days_to_zero >= 90:  status = "HIGH_RISK"
            elif days_to_zero >= 30:  status = "CRITICAL"
            else:                     status = "ACUTE_CRISIS"

        remaining = max(0.0, inv - net * min(horizon, days_to_zero
                        if days_to_zero != math.inf else horizon))
        pct_rem   = round(remaining / inv * 100, 1) if inv > 0 else 0.0
        surge     = max(0, int((daily - d_prod) * 365))

        inv_value = inv * ws.get("unit_cost",
                    ws.get("unit_cost_per_shot", 0))

        results.append({
            "system":           key,
            "tier":             ws.get("tier", "—"),
            "inventory":        inv,
            "inventory_value_B": round(inv_value / 1e9, 2),
            "daily_consumption": daily,
            "daily_production": round(d_prod, 1),
            "net_daily_draw":   round(net, 1),
            "days_to_zero":     round(days_to_zero, 1) if days_to_zero != math.inf else "∞",
            "pct_at_horizon":   pct_rem,
            "status":           status,
            "annual_surge_units": surge,
            "surge_cost_B":     round(surge * ws.get("unit_cost", 0) / 1e9, 2),
        })
        log.debug("Depletion %s: net=%.1f/day  days_to_zero=%s  status=%s",
                  key, net,
                  f"{days_to_zero:.0f}" if days_to_zero != math.inf else "∞",
                  status)

    results.sort(key=lambda r: (
        float("inf") if r["days_to_zero"] == "∞"
        else r["days_to_zero"]
    ))
    log.info("Two-war depletion: %d systems analysed, horizon=%d days",
             len(results), horizon)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — Marginal Value: Coverage-Days per Dollar
# For each system: how many additional days of coverage does $X buy?
# ─────────────────────────────────────────────────────────────────────────────

def marginal_value(cfg: Config,
                   budget_increments_M: list[float] | None = None) -> list[dict]:
    """
    Compute coverage-days gained per $100M and $1B for each consumable system.
    Uses the deterministic (mean) consumption rates — MC version in mc_simulator.py.

    Returns list sorted descending by days_per_100M (best ROI first).
    """
    increments = budget_increments_M or [100.0, 1_000.0]
    results    = []

    for key, ws in cfg.consumable_systems().items():
        cr      = ws["consumption_rates"]
        daily   = cr["theater_1"]["mean"] + cr["theater_2"]["mean"]
        if daily <= 0:
            continue

        unit_cost = ws.get("unit_cost",
                    ws.get("unit_cost_per_shot", 0))
        if unit_cost <= 0:
            continue

        annual = ws.get("annual_production",
                 ws.get("annual_production_target", 0))
        d_prod = annual / 365.0
        net    = max(0.0, daily - d_prod)

        gains = {}
        for bM in increments:
            units_added  = bM * 1e6 / unit_cost
            days_gained  = units_added / net if net > 0 else float("inf")
            gains[f"days_per_{int(bM)}M"] = (
                round(days_gained, 1) if days_gained != float("inf") else "∞"
            )

        results.append({
            "system":      key,
            "tier":        ws.get("tier", "—"),
            "unit_cost":   unit_cost,
            "quality":     ws.get("quality_tier", "—"),
            "dud_pct":     round(ws.get("dud_rate", 0) * 100, 1),
            **gains,
        })

    # Sort by days per $100M (descending)
    def _sort_key(r):
        v = r.get("days_per_100M", 0)
        return float("inf") if v == "∞" else (v if isinstance(v, float) else 0)

    results.sort(key=_sort_key, reverse=True)
    log.info("Marginal value: %d systems ranked", len(results))
    return results
