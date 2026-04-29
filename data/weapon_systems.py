"""
Weapon Systems Cost and Inventory Database
Paper 6: The Cost Curve as Deterrent
Sources: CRS, CSIS Missile Defense Project, SAR FY2025/2026, CENTCOM, DoD budget docs
All costs in USD. Inventory figures from open-source estimates as of April 2026.
"""

WEAPON_SYSTEMS = {

    # ── TIER 1: HIGH-END INTERCEPTORS (strategic scarcity assets) ──────────────
    "THAAD": {
        "type": "interceptor_ballistic",
        "unit_cost": 12_700_000,        # FY2025 MDA budget; $15M FY2026 estimate
        "inventory_est": 370,           # Post-Epic-Fury estimate (down from ~632)
        "inventory_value": 370 * 12_700_000,
        "annual_production": 32,        # FY2026 request; was 12 in FY2025
        "time_to_replace_years": (3, 8),  # CRS estimate range
        "engagement_range_km": 200,
        "intercept_rate_pct": 90,       # CSIS estimate vs. MRBMs
        "systems_defended": "MRBM/IRBM terminal phase",
        "batteries": 8,
        "cost_per_battery": 2_730_000_000,  # AEI estimate incl. 192 interceptors
        "notes": "Deliveries paused Aug 2023–Apr 2027; strategic scarcity asset",
        "source": "CRS IF12645; CSIS Missile Defense Project; JINSA 2025",
    },

    "SM3_IIA": {
        "type": "interceptor_midcourse",
        "unit_cost": 24_000_000,        # FY2024 supplemental; was $9M in FY2021
        "inventory_est": 150,           # Post-2025/2026 drawdown estimate
        "inventory_value": 150 * 24_000_000,
        "annual_production": 20,        # MDA FY2026 budget request
        "time_to_replace_years": (4, 6),
        "engagement_range_km": 700,
        "intercept_rate_pct": 85,
        "systems_defended": "MRBM/IRBM midcourse phase",
        "notes": "Cost nearly tripled FY2021→FY2024 due to production uncertainty",
        "source": "CSIS Missile Defense Project; MDA budget exhibits",
    },

    "PAC3_MSE": {
        "type": "interceptor_tactical",
        "unit_cost": 3_700_000,         # JINSA 2025 estimate
        "inventory_est": 1_200,         # Rough estimate; classified
        "inventory_value": 1_200 * 3_700_000,
        "annual_production": 500,       # Current; ramp to 2,000/yr by 2027
        "time_to_replace_years": (0.5, 2),
        "engagement_range_km": 35,
        "intercept_rate_pct": 80,
        "systems_defended": "SRBM/cruise missile terminal phase",
        "notes": "Lockheed Martin ramp to 650/yr announced; 2,000/yr target by 2027",
        "source": "JINSA 2025; Lockheed Martin investor briefings",
    },

    "SM2": {
        "type": "interceptor_air_defense",
        "unit_cost": 2_000_000,
        "inventory_est": 3_000,
        "inventory_value": 3_000 * 2_000_000,
        "annual_production": 200,
        "time_to_replace_years": (1, 3),
        "engagement_range_km": 170,
        "intercept_rate_pct": 75,
        "systems_defended": "Aircraft, cruise missiles, ASMs",
        "notes": "Workhorse Aegis interceptor; large stockpile but aging",
        "source": "SAR annual updates; CRS",
    },

    "SM6": {
        "type": "interceptor_multi_mission",
        "unit_cost": 4_300_000,
        "inventory_est": 800,
        "inventory_value": 800 * 4_300_000,
        "annual_production": 125,
        "time_to_replace_years": (2, 4),
        "engagement_range_km": 370,
        "intercept_rate_pct": 82,
        "systems_defended": "Aircraft, cruise missiles, terminal ballistic",
        "notes": "Dual-role: can engage surface targets; key Indo-Pacific asset",
        "source": "SAR; CSIS",
    },

    # ── TIER 2: OFFENSIVE PRECISION STRIKE ────────────────────────────────────
    "Tomahawk_TLAM": {
        "type": "cruise_missile_offensive",
        "unit_cost": 2_100_000,
        "inventory_est": 4_000,
        "inventory_value": 4_000 * 2_100_000,
        "annual_production": 350,
        "time_to_replace_years": (1, 3),
        "engagement_range_km": 1_600,
        "intercept_rate_pct": None,     # offensive
        "systems_defended": None,
        "notes": "Launched from surface ships and submarines; GPS-guided",
        "source": "SAR; CRS RL30563",
    },

    "JASSM_ER": {
        "type": "air_launched_cruise_missile",
        "unit_cost": 1_500_000,
        "inventory_est": 3_500,
        "inventory_value": 3_500 * 1_500_000,
        "annual_production": 600,
        "time_to_replace_years": (1, 2),
        "engagement_range_km": 980,
        "intercept_rate_pct": None,
        "systems_defended": None,
        "notes": "Stealth cruise missile; low radar cross-section",
        "source": "SAR; USAF budget docs",
    },

    # ── TIER 3: ATTRITABLE / LOW-COST OFFENSIVE DRONES ───────────────────────
    "LUCAS": {
        "type": "one_way_attack_drone",
        "unit_cost": 35_000,            # CENTCOM confirmed
        "unit_cost_future": 5_000,      # Drone Dominance Programme Phase IV target
        "inventory_est": 5_000,         # Estimated post-initial production
        "inventory_value": 5_000 * 35_000,
        "annual_production_target": 300_000,  # Drone Dominance Programme goal
        "time_to_replace_years": 0,     # Days-to-weeks at scale
        "engagement_range_km": 800,
        "intercept_rate_pct": None,
        "systems_defended": None,
        "notes": "Reverse-engineered Shahed-136; first combat use Feb 28 2026; $35K vs $2.1M Tomahawk = 60:1 cost ratio",
        "source": "CENTCOM; drone-warfare.com March 2026; dsm.forecastinternational.com",
    },

    "FPV_Quadcopter": {
        "type": "fpv_attack_drone",
        "unit_cost": 800,               # Mid-range FPV; Ukraine battlefield estimate
        "unit_cost_range": (400, 2_000),
        "inventory_est": 50_000,        # Target for two-war scenario
        "inventory_value": 50_000 * 800,
        "annual_production_target": 1_000_000,
        "time_to_replace_years": 0,
        "engagement_range_km": 10,
        "intercept_rate_pct": None,
        "systems_defended": None,
        "notes": "Short-range tactical; proven in Ukraine; battlefield logistics disruptor",
        "source": "Open-source Ukraine OSINT; DIU briefings",
    },

    "Switchblade_600": {
        "type": "loitering_munition",
        "unit_cost": 100_000,           # Estimated; classified
        "inventory_est": 5_000,
        "inventory_value": 5_000 * 100_000,
        "annual_production": 2_000,
        "time_to_replace_years": 0,
        "engagement_range_km": 40,
        "intercept_rate_pct": None,
        "systems_defended": None,
        "notes": "Anti-armor capable; man-portable; Replicator included",
        "source": "CRS IF12611; Responsible Statecraft",
    },

    # ── TIER 4: COUNTER-DRONE (C-UAS) ─────────────────────────────────────────
    "DroneHunter": {
        "type": "c_uas_interceptor_drone",
        "unit_cost": 15_000,
        "inventory_est": 2_000,
        "inventory_value": 2_000 * 15_000,
        "annual_production_target": 50_000,
        "time_to_replace_years": 0,
        "engagement_range_km": 5,
        "intercept_rate_pct": 70,       # Estimated vs. Group 1/2 UAS
        "systems_defended": "FPV drones, Group 1/2 UAS",
        "notes": "Drone-vs-drone; proven in Ukraine; nets or kinetic intercept; $15K vs $35K LUCAS = favorable CAR",
        "source": "Open-source Ukraine OSINT; DIU C-UAS briefings",
    },

    "Iron_Beam_DEW": {
        "type": "directed_energy_laser",
        "unit_cost_per_shot": 2,        # Estimated $/engagement (laser electricity cost)
        "system_cost": 20_000_000,      # Per unit; Elbit/Rafael estimate
        "inventory_est": 12,            # Limited operational fielding (Israel)
        "annual_production_target": 100,
        "time_to_replace_years": (1, 3),
        "engagement_range_km": 7,
        "intercept_rate_pct": 90,       # vs. drones/rockets; confirmed Lebanon 2026
        "systems_defended": "Rockets, drones, mortars (SHORAD)",
        "notes": "Per-shot cost ~$2 vs $3.7M PAC-3 = structural CAR solution; limited range",
        "source": "Norskluftvern.com March 2026; Iron Beam operational reports",
    },

    "HELIOS_Navy_DEW": {
        "type": "directed_energy_laser_naval",
        "unit_cost_per_shot": 1,
        "system_cost": 150_000_000,     # Lockheed HELIOS programme
        "inventory_est": 4,             # Ships with operational systems
        "time_to_replace_years": (2, 5),
        "engagement_range_km": 5,
        "intercept_rate_pct": 85,
        "systems_defended": "Small UAS, small boats, optical sensors",
        "notes": "USS Preble operational; 60kW; scalable to 150kW",
        "source": "Lockheed Martin; Navy budget docs",
    },
}

# ── ADVERSARY THREAT SYSTEMS (for CAR computation) ────────────────────────────
THREAT_SYSTEMS = {
    "Shahed_136": {
        "unit_cost": 20_000,            # Iranian production cost estimate
        "range_km": 2_000,
        "warhead_kg": 50,
        "notes": "One-way attack drone; mass-producible; core Houthi weapon",
    },
    "Iranian_Ballistic_Missile_MRBM": {
        "unit_cost": 3_000_000,         # Estimate (Shahab-3 class)
        "range_km": 2_000,
        "warhead_kg": 750,
        "notes": "Primary Epic Fury threat; depletes THAAD/SM-3 stocks",
    },
    "FPV_Adversary": {
        "unit_cost": 500,
        "range_km": 10,
        "warhead_kg": 1,
        "notes": "Used by Iran proxies; $500 drone vs $3.7M PAC-3 = 7,400:1 CAR",
    },
    "Hypersonic_Glide_China": {
        "unit_cost": 10_000_000,        # DF-17 estimate
        "range_km": 2_000,
        "warhead_kg": 500,
        "notes": "No current US interceptor; structural capability gap",
    },
}
