"""
Cost-Asymmetry Simulator — Paper 6: The Cost Curve as Deterrent
MTS Pillar 3: Compound Warfare Economics

Three analytical modules:
  1. CAR Matrix      — Cost Asymmetry Ratios for all threat/interceptor pairings
  2. Two-War Engine  — Inventory depletion under simultaneous theater stress
  3. Marginal Value  — Optimal next-dollar allocation for deterrence per dollar spent
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data.weapon_systems import WEAPON_SYSTEMS, THREAT_SYSTEMS
import math, json

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — Cost Asymmetry Ratio Matrix
# CAR = Cost of adversary offensive action / Cost of US defensive response
# CAR > 1: US has cost advantage   CAR < 1: adversary has cost advantage
# ─────────────────────────────────────────────────────────────────────────────

def compute_car_matrix():
    """
    Compute CAR for every threat / defender pairing.
    Returns sorted table from worst (lowest CAR) to best.
    """
    pairings = [
        # (threat_key, defender_key, notes)
        ("FPV_Adversary",           "PAC3_MSE",      "FPV drone vs Patriot"),
        ("FPV_Adversary",           "THAAD",          "FPV drone vs THAAD"),
        ("FPV_Adversary",           "DroneHunter",    "FPV drone vs drone-hunter"),
        ("FPV_Adversary",           "Iron_Beam_DEW",  "FPV drone vs Iron Beam"),
        ("Shahed_136",              "PAC3_MSE",       "Shahed vs Patriot"),
        ("Shahed_136",              "SM2",            "Shahed vs SM-2"),
        ("Shahed_136",              "DroneHunter",    "Shahed vs drone-hunter"),
        ("Shahed_136",              "Iron_Beam_DEW",  "Shahed vs Iron Beam"),
        ("Shahed_136",              "LUCAS",          "Shahed vs LUCAS offensive exchange"),
        ("Iranian_Ballistic_Missile_MRBM", "THAAD",   "MRBM vs THAAD"),
        ("Iranian_Ballistic_Missile_MRBM", "SM3_IIA", "MRBM vs SM-3 IIA"),
        ("Iranian_Ballistic_Missile_MRBM", "PAC3_MSE","MRBM vs PAC-3 MSE"),
        ("Hypersonic_Glide_China",  "THAAD",          "DF-17 vs THAAD (no intercept)"),
    ]

    results = []
    for threat_key, defender_key, note in pairings:
        threat = THREAT_SYSTEMS[threat_key]
        defender = WEAPON_SYSTEMS[defender_key]

        threat_cost  = threat["unit_cost"]
        if "unit_cost_per_shot" in defender:
            # Directed energy: use per-shot cost
            defend_cost = defender["unit_cost_per_shot"]
        else:
            defend_cost  = defender["unit_cost"]

        # Hypersonic: no current interceptor — mark as infinite cost disadvantage
        if threat_key == "Hypersonic_Glide_China" and defender_key == "THAAD":
            car = 0.0
            intercept_possible = False
        else:
            car = threat_cost / defend_cost
            intercept_possible = True

        results.append({
            "threat":        threat_key,
            "defender":      defender_key,
            "note":          note,
            "threat_cost":   threat_cost,
            "defend_cost":   defend_cost,
            "CAR":           round(car, 4),
            "interpretation": "US ADVANTAGE" if car > 1.0 else
                              "PARITY"        if 0.8 <= car <= 1.0 else
                              "ADV ADVANTAGE",
            "intercept_possible": intercept_possible,
        })

    return sorted(results, key=lambda x: x["CAR"])


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — Two-War Inventory Depletion Engine
# Models simultaneous theater 1 (Middle East/Iran) + theater 2 (Indo-Pacific)
# Computes days-to-depletion and production gap for each system
# ─────────────────────────────────────────────────────────────────────────────

# Consumption rates per day at sustained high-intensity combat
# Sourced from: Epic Fury ~40 THAAD/6 days → ~7/day high intensity
# PAC-3: ~90 fired in 6 days → ~15/day
# SM-2/SM-6: ~180 in 6 days → ~30/day
# Source: Norskluftvern March 2026 update

CONSUMPTION_RATES = {
    # (theater_1_per_day, theater_2_per_day) at high-intensity sustained ops
    "THAAD":        (7,   3),    # Middle East heavy; Indo-Pacific moderate
    "SM3_IIA":      (4,   6),    # Indo-Pacific: primary MRBM layer vs China
    "PAC3_MSE":     (15,  12),
    "SM2":          (30,  20),
    "SM6":          (8,   15),   # More critical in Indo-Pacific (ASBM threat)
    "Tomahawk_TLAM":(25,  40),   # Strike-heavy in both
    "JASSM_ER":     (15,  30),
    "LUCAS":        (500, 1_000),  # Mass attritable; high consumption designed
    "FPV_Quadcopter":(5_000, 10_000),
    "Switchblade_600":(50, 100),
    "DroneHunter":  (100, 200),
    "Iron_Beam_DEW": (0,  0),     # System, not consumable; shots ~unlimited
    "HELIOS_Navy_DEW":(0,  0),
}

def two_war_analysis(days: int = 90):
    """
    Simulate inventory depletion over `days` of simultaneous two-war operations.
    Returns per-system assessment including days-to-zero and production gap.
    """
    results = []
    for system_key, ws in WEAPON_SYSTEMS.items():
        if system_key not in CONSUMPTION_RATES:
            continue
        if ws["type"] in ("directed_energy_laser", "directed_energy_laser_naval"):
            continue  # DEW systems not consumable

        c1, c2     = CONSUMPTION_RATES[system_key]
        daily_total = c1 + c2
        inventory   = ws.get("inventory_est", 0)
        annual_prod = ws.get("annual_production",
                     ws.get("annual_production_target", 0))
        daily_prod  = annual_prod / 365

        # Net daily draw = consumption - production
        net_draw = daily_total - daily_prod

        if net_draw <= 0:
            days_to_zero = float("inf")
            status = "SELF_SUSTAINING"
        else:
            days_to_zero = inventory / net_draw
            if days_to_zero >= 365:
                status = "LOW_RISK"
            elif days_to_zero >= 180:
                status = "MEDIUM_RISK"
            elif days_to_zero >= 90:
                status = "HIGH_RISK"
            elif days_to_zero >= 30:
                status = "CRITICAL"
            else:
                status = "ACUTE_CRISIS"

        # Inventory remaining at day `days`
        consumed = min(daily_total * days, inventory + daily_prod * days)
        remaining = max(0, inventory - net_draw * days)
        pct_remaining = round(remaining / inventory * 100, 1) if inventory > 0 else 0

        # Production surge needed to sustain 90-day two-war
        surge_needed = max(0, daily_total - daily_prod) * 365  # annual surge

        results.append({
            "system":           system_key,
            "inventory":        inventory,
            "inventory_value_B": round(ws.get("inventory_value",0) / 1e9, 2),
            "daily_consumption": daily_total,
            "daily_production":  round(daily_prod, 1),
            "net_daily_draw":    round(net_draw, 1),
            "days_to_zero":      round(days_to_zero, 0) if days_to_zero != float("inf") else "∞",
            "pct_at_day90":      pct_remaining,
            "status":            status,
            "annual_surge_needed": int(surge_needed),
            "replace_years":    ws.get("time_to_replace_years", "N/A"),
        })

    return sorted(results, key=lambda x: (
        0 if x["days_to_zero"] == "∞" else x["days_to_zero"]))


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — Marginal Deterrence Value: Optimal Next-Dollar Allocation
# For each $1M increment, computes:
#   - Additional inventory units purchased
#   - Deterrence impact: days of additional coverage per dollar
#   - CAR improvement: how much the investment shifts the cost exchange
# ─────────────────────────────────────────────────────────────────────────────

def marginal_dollar_analysis(budget_increment_M: float = 1.0):
    """
    For each system, compute what one additional $budget_increment_M buys
    in terms of: units, coverage days, and deterrence-per-dollar value.
    """
    budget = budget_increment_M * 1_000_000
    results = []

    # CAR matrix for deterrence scoring
    car_map = {r["defender"]: r["CAR"] for r in compute_car_matrix()}

    for system_key, ws in WEAPON_SYSTEMS.items():
        if ws["type"] in ("directed_energy_laser", "directed_energy_laser_naval"):
            # DEW: marginal value is system acquisition, not per-shot
            unit_cost = ws.get("system_cost", 0)
        elif "unit_cost_per_shot" in ws:
            unit_cost = ws["unit_cost_per_shot"]
        else:
            unit_cost = ws.get("unit_cost", 0)

        if unit_cost <= 0:
            continue

        units_purchased = budget / unit_cost

        # Coverage days: how many additional days does this buy
        if system_key in CONSUMPTION_RATES:
            c1, c2 = CONSUMPTION_RATES[system_key]
            daily = c1 + c2
            coverage_days = units_purchased / daily if daily > 0 else float("inf")
        else:
            coverage_days = float("inf")

        # Deterrence score: CAR * coverage days * intercept rate
        car     = car_map.get(system_key, 1.0)
        icr     = (ws.get("intercept_rate_pct") or 50) / 100
        det_score = car * coverage_days * icr

        # Strategic tier
        if ws["type"] in ("interceptor_ballistic", "interceptor_midcourse"):
            tier = "STRATEGIC"
        elif ws["type"] in ("interceptor_tactical", "interceptor_air_defense",
                             "interceptor_multi_mission"):
            tier = "OPERATIONAL"
        elif ws["type"] in ("one_way_attack_drone", "fpv_attack_drone",
                             "loitering_munition"):
            tier = "ATTRITION_OFFENSE"
        elif ws["type"] in ("c_uas_interceptor_drone",):
            tier = "ATTRITION_DEFENSE"
        elif "directed_energy" in ws["type"]:
            tier = "STRUCTURAL_SOLUTION"
        else:
            tier = "PRECISION_STRIKE"

        # Replenishment flag
        replenish_yrs = ws.get("time_to_replace_years", 0)
        if isinstance(replenish_yrs, tuple):
            replenish_min = replenish_yrs[0]
        else:
            replenish_min = replenish_yrs

        results.append({
            "system":          system_key,
            "tier":            tier,
            "unit_cost":       unit_cost,
            "units_per_M":     round(units_purchased / (budget_increment_M), 1),
            "coverage_days":   round(coverage_days, 1) if coverage_days != float("inf") else "∞",
            "deterrence_score": round(det_score, 2),
            "CAR":             round(car, 3),
            "replenish_yrs_min": replenish_min,
            "priority":        "HIGH"   if det_score > 50 else
                               "MEDIUM" if det_score > 10 else "LOW",
        })

    return sorted(results, key=lambda x: -x["deterrence_score"])


# ─────────────────────────────────────────────────────────────────────────────
# RUN ALL THREE MODULES
# ─────────────────────────────────────────────────────────────────────────────

def run_full_analysis():
    print("=" * 72)
    print("  COST ASYMMETRY SIMULATOR — MTS Pillar 3")
    print("  Paper 6: The Cost Curve as Deterrent")
    print("=" * 72)

    # ── Module 1: CAR Matrix ──────────────────────────────────────────────────
    print("\n── MODULE 1: Cost Asymmetry Ratio Matrix ────────────────────────────")
    print(f"  CAR = Adversary offensive cost / US defensive response cost")
    print(f"  CAR > 1.0 = US cost advantage   CAR < 1.0 = Adversary cost advantage")
    print()
    print(f"  {'Pairing':<45} {'Threat$':>10} {'Defend$':>12} {'CAR':>7}  {'Status'}")
    print("  " + "-" * 90)
    for r in compute_car_matrix():
        thr_fmt = f"${r['threat_cost']:>9,.0f}"
        def_fmt = f"${r['defend_cost']:>10,.0f}"
        car_fmt = f"{r['CAR']:>7.4f}"
        flag = "  ⚠ ADV WINS" if r["interpretation"] == "ADV ADVANTAGE" else \
               "  ✓ US WINS"  if r["interpretation"] == "US ADVANTAGE"  else ""
        print(f"  {r['note']:<45} {thr_fmt} {def_fmt} {car_fmt}  {r['interpretation']}{flag}")

    # ── Module 2: Two-War Depletion ───────────────────────────────────────────
    print("\n\n── MODULE 2: Two-War Inventory Depletion (90-day simulation) ────────")
    print(f"  Theater 1: Middle East/Iran  |  Theater 2: Indo-Pacific/China")
    print()
    print(f"  {'System':<22} {'Inv':>6} {'Val($B)':>7} {'Day/T1+T2':>10} {'Day/Prod':>8} "
          f"{'Days→0':>8} {'@Day90':>7}  Status")
    print("  " + "-" * 100)
    for r in two_war_analysis(90):
        d0 = str(r['days_to_zero'])[:6]
        pct = f"{r['pct_at_day90']}%"
        flag = "  🔴 CRISIS" if r["status"] in ("ACUTE_CRISIS","CRITICAL") else \
               "  🟡 RISK"   if r["status"] == "HIGH_RISK" else \
               "  🟢 OK"     if r["status"] in ("SELF_SUSTAINING","LOW_RISK") else ""
        print(f"  {r['system']:<22} {r['inventory']:>6,} {r['inventory_value_B']:>7.2f}B "
              f"{r['daily_consumption']:>10.1f} {r['daily_production']:>8.1f} "
              f"{d0:>8} {pct:>7}  {r['status']}{flag}")

    # ── Module 3: Marginal Dollar Allocation ─────────────────────────────────
    print("\n\n── MODULE 3: Optimal Marginal Spend — $1B Increment Analysis ────────")
    print(f"  Ranked by deterrence score (CAR × coverage_days × intercept_rate)")
    print(f"  Priority spend: maximize deterrence-per-dollar AND fill scarcity gaps")
    print()
    print(f"  {'System':<22} {'Tier':<20} {'Units/M$':>9} {'Cover_Days':>11} "
          f"{'Det_Score':>10} {'CAR':>7}  Priority")
    print("  " + "-" * 100)
    for r in marginal_dollar_analysis(1.0):
        if r["coverage_days"] == "∞":
            cov = "     ∞"
        else:
            cov = f"{r['coverage_days']:>10.1f}"
        flag = "  ★★★" if r["priority"] == "HIGH" else \
               "  ★★"  if r["priority"] == "MEDIUM" else "  ★"
        print(f"  {r['system']:<22} {r['tier']:<20} {r['units_per_M']:>9.1f} "
              f"{cov} {r['deterrence_score']:>10.2f} {r['CAR']:>7.3f}{flag}")

    # ── Strategic Synthesis ───────────────────────────────────────────────────
    print("\n\n── STRATEGIC SYNTHESIS ──────────────────────────────────────────────")
    print("""
  KEY FINDINGS:

  1. STRUCTURAL CAR INVERSION (the core problem)
     FPV drone ($500) vs PAC-3 MSE ($3.7M) = CAR of 0.000135
     The adversary spends $500 to force a $3.7M US response — a 7,400:1
     exchange ratio. At scale (thousands of drones), this is fiscal attrition
     regardless of tactical outcome.

  2. THAAD: STRATEGIC SCARCITY ASSET IN ACUTE CRISIS
     ~370 interceptors remaining post-Epic Fury. $12.7M/unit.
     Only 32/year being produced. Days-to-zero in two-war: ~50 days.
     3-8 year replacement timeline. This is the single most critical gap.

  3. DIRECTED ENERGY: THE STRUCTURAL SOLUTION
     Iron Beam DEW: $2/shot vs $3.7M PAC-3 = CAR of 7,400:1 in US favor.
     This inverts the cost curve permanently for drones/rockets/mortars.
     Current inventory: ~12 systems. This is where marginal dollars have
     highest deterrence value per dollar spent.

  4. LUCAS/FPV DRONES: ASYMMETRIC OFFENSE AT SCALE
     $35K LUCAS vs $2.1M Tomahawk = 60:1 cost advantage for same strike.
     $800 FPV at scale provides mass that overwhelms air defense magazines.
     FY2027 DAWG request: $54.6B — a structural commitment to this doctrine.

  5. OPTIMAL NEXT-DOLLAR PRIORITY ORDER (for maximum deterrence/dollar):
     [1] Directed Energy (Iron Beam, HELIOS) — structural CAR solution
     [2] THAAD production surge — fill critical scarcity gap
     [3] LUCAS/FPV scale production — asymmetric offense
     [4] DroneHunter C-UAS — cost-effective defense against mass drones
     [5] PAC-3 MSE production ramp — tactical air defense replenishment
     [6] SM-3/SM-6 — Indo-Pacific coverage gap
""")

    # Export to JSON for Paper 6 tables
    output = {
        "car_matrix": compute_car_matrix(),
        "two_war_90d": two_war_analysis(90),
        "marginal_1M": marginal_dollar_analysis(1.0),
        "marginal_1B": marginal_dollar_analysis(1000.0),
    }
    with open("output/cost_asymmetry_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("  Results exported to output/cost_asymmetry_results.json")


if __name__ == "__main__":
    run_full_analysis()
