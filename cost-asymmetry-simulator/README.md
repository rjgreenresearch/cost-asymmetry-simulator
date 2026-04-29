# Cost Asymmetry Simulator

**Compound Warfare Economics — Simulation Tool for Cost-Curve Deterrence Analysis**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-planned_100+-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()

## Overview

The Cost Asymmetry Simulator models compound warfare cost dynamics across five domains: offense-defense cost imbalance, attrition-replacement disparity, industrial tempo mismatch, economic cascade costs, and reconstruction burden. It computes the Cost Asymmetry Ratio (CAR), simulates engagement cost exchanges, and evaluates compound deterrence stability.

This tool is the companion software for:

> Green, R.J. (2026) "The Cost Curve as Deterrent: Compound Warfare Economics, Saturation Dynamics, and the Structural Unaffordability of Great-Power Conflict." Working Paper. *International Security* (target).

It implements the third pillar of the Mutual Threshold Saturation (MTS) unified deterrence architecture.

## Three-Pillar MTS Architecture

| Pillar | Domain | Tool | Paper |
|--------|--------|------|-------|
| 1. Material MTS | Supply chain compound dependencies | [mts-doctrine-simulator](https://github.com/rjgreenresearch/mts-doctrine-simulator) | Green (2026d) |
| 2. Human Capital MTS | Key-person institutional fragility | [hcts-simulator](https://github.com/rjgreenresearch/hcts-simulator) | Green (2026e) |
| **3. Cost Asymmetry MTS** | **Compound warfare economics** | **cost-asymmetry-simulator (this repo)** | **Green (2026f)** |

## Core Capabilities

**Cost Asymmetry Ratio (CAR):** Measures the cost-exchange ratio between offensive and defensive systems. A CAR of 1:50 means the attacker spends $1 for every $50 the defender must spend. When the attacker can produce at industrial scale, unfavorable CARs become strategically decisive.

**Five-Domain Taxonomy:**
- **Offense-Defense Imbalance:** Drone vs interceptor cost exchange ($20K OWA vs $4M SM-6)
- **Attrition-Replacement Disparity:** Platform loss vs replacement timeline (F-35: 3-5 years)
- **Industrial Tempo Mismatch:** Weeks (drones) vs decades (carriers) production cycles
- **Economic Cascade Costs:** Trade disruption multiplied across dependent sectors
- **Reconstruction Burden:** Post-conflict fiscal obligations (Iraq/Afghanistan: $8T+)

**Simulation Engines:**
- Day-by-day engagement cost exchange with magazine depletion
- Compound conflict cost across all five domains simultaneously
- Deterrence threshold assessment (expected cost vs expected gain)
- Three-pillar integration with Material MTS and Human Capital MTS

**Pre-Built Scenarios:**
- Operation Epic Fury (Houthi Red Sea cost exchange)
- Taiwan Strait compound scenario (all five domains)
- Drone saturation defense (interceptor-only vs DEW-augmented)
- A-10 vs F-35 cost-exchange comparison (legacy modernization case)

## Installation

```bash
git clone https://github.com/rjgreenresearch/cost-asymmetry-simulator.git
cd cost-asymmetry-simulator
pip install -r requirements.txt
```

## Quick Start

```python
from cost_asymmetry_simulator import WeaponSystem, Category
from cost_asymmetry_simulator.analysis import compute_car
from cost_asymmetry_simulator.simulation import simulate_engagement_exchange

# Define offense-defense pair
shahed_136 = WeaponSystem(
    id="shahed_136", name="Shahed-136 OWA",
    category=Category.OFFENSIVE,
    unit_cost_usd=30_000,
    marginal_engagement_cost=30_000,
    production_time_months=0.5,
    max_monthly_production=500
)

sm6 = WeaponSystem(
    id="sm6", name="Standard Missile-6",
    category=Category.DEFENSIVE,
    unit_cost_usd=4_300_000,
    marginal_engagement_cost=4_300_000,
    production_time_months=18,
    max_monthly_production=30
)

# Compute Cost Asymmetry Ratio
car = compute_car(shahed_136, sm6)
print(f"CAR: 1:{car.ratio:.0f} in attacker's favor")

# Simulate 90-day engagement exchange
result = simulate_engagement_exchange(
    offense=[shahed_136],
    defense=[sm6],
    attack_tempo=5,  # 5 attacks per day
    duration_days=90
)
result.plot_cost_trajectories()
print(f"Defender budget exhaustion: day {result.defender_exhaustion_day}")
```

## Repository Structure

```
cost-asymmetry-simulator/
├── README.md
├── LICENSE                          # Apache 2.0
├── CITATION.cff
├── SPECIFICATION.md                 # Full technical specification
├── DATA_ACQUISITION.md              # Data source catalog
├── requirements.txt
├── setup.py
│
├── cost_asymmetry_simulator/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── weapon_system.py         # WeaponSystem data model
│   │   ├── conflict_scenario.py     # ConflictScenario model
│   │   └── cost_ratio.py            # CostAsymmetryRatio model
│   ├── cost_models/
│   │   ├── __init__.py
│   │   ├── offense_defense.py       # CAR computation per system pair
│   │   ├── attrition_replacement.py # Platform loss/replacement modeling
│   │   ├── industrial_tempo.py      # Production cycle comparison
│   │   ├── economic_cascade.py      # Cross-sector disruption costs
│   │   └── reconstruction.py        # Post-conflict fiscal burden
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── engagement.py            # Day-by-day cost exchange
│   │   ├── compound_cost.py         # Five-domain compound simulation
│   │   └── deterrence.py            # Deterrence threshold assessment
│   ├── compound/
│   │   ├── __init__.py
│   │   ├── three_pillar.py          # Material + Human Capital + Cost
│   │   └── integration.py           # mts-core interface
│   └── export/
│       ├── __init__.py
│       ├── csv_export.py
│       └── visualisation.py
│
├── data/
│   ├── weapon_systems.csv           # Standardized system costs from SARs/J-Books
│   ├── interceptor_costs.csv        # Missile defense system costs
│   ├── drone_costs.csv              # OWA and adversary UAS costs
│   ├── engagement_log_epic_fury.csv # CENTCOM Red Sea engagement data
│   └── deflators.csv                # DoD Green Book constant-dollar deflators
│
├── scenarios/
│   ├── epic_fury.yaml
│   ├── taiwan_strait.yaml
│   ├── drone_saturation.yaml
│   └── legacy_comparison.yaml
│
├── tests/
│   ├── test_models.py               # 15 tests
│   ├── test_engagement.py           # 20 tests
│   ├── test_compound_cost.py        # 20 tests
│   ├── test_deterrence.py           # 15 tests
│   ├── test_scenarios.py            # 15 tests
│   ├── test_integration.py          # 10 tests
│   └── test_export.py               # 5 tests
│
└── docs/
    ├── methodology.md
    ├── data_sources.md
    └── examples/
```

## Data Sources

All cost data is derived from primary U.S. government sources. Key sources include DoD Selected Acquisition Reports (SARs), Comptroller Budget Justification Documents (J-Books), CENTCOM press releases for Operation Epic Fury engagement data, CRS independent cost analyses, GAO industrial base assessments, and the Brown University Costs of War Project. Full documentation in DATA_ACQUISITION.md.

## Testing

```bash
pytest tests/ -v
```

Target: 100+ automated tests across data model validation, CAR computation, engagement exchange simulation, compound cost modeling, deterrence assessment, scenario validation, and three-pillar integration.

## Related Research

This tool is part of a six-paper research programme on Mutual Threshold Saturation:

1. Green (2026a) — Spatial Clustering. DOI: [10.2139/ssrn.6454202](https://doi.org/10.2139/ssrn.6454202)
2. Green (2026b) — Ownership Visibility. DOI: [10.2139/ssrn.6520499](https://doi.org/10.2139/ssrn.6520499)
3. Green (2026c) — Regulatory Perimeter. DOI: [10.2139/ssrn.6525938](https://doi.org/10.2139/ssrn.6525938)
4. Green (2026d) — Supply Chain Dependencies / Material MTS. DOI: [10.2139/ssrn.6454618](https://doi.org/10.2139/ssrn.6454618)
5. Green (2026e) — Human Capital Threshold Saturation
6. Green (2026f) — Cost Asymmetry Doctrine (this tool's companion paper)

## Author

**Robert J. Green**
Independent Researcher | Former U.S. Army Air Defense Artillery Officer
MBA, University of Central Florida | BA, Philosophy and Leadership Studies
ORCID: [0009-0002-9097-1021](https://orcid.org/0009-0002-9097-1021)
Website: [rjgreenresearch.org](https://rjgreenresearch.org)

## License

Apache 2.0. See [LICENSE](LICENSE).

## Citation

If you use this tool in your research, please cite both the software and the companion paper. See [CITATION.cff](CITATION.cff).
