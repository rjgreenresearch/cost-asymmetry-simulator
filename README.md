# Cost-Asymmetry Simulator (CAS)
### MTS Pillar 3 — Paper 6: *The Cost Curve as Deterrent*

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![SSRN](https://img.shields.io/badge/SSRN-forthcoming-orange.svg)](https://ssrn.com)

A Monte Carlo inventory optimisation simulator for U.S. military munitions,
implementing the **Dyna-METRIC readiness-based sparing framework** adapted for
consumable weapons systems. Produces Cost Asymmetry Ratio (CAR) matrices,
two-war depletion timelines, and marginal-value portfolio allocation guidance.

---

## What it does

CAS answers three policy questions central to U.S. defence economics:

1. **Can the U.S. fight two wars simultaneously?**
   — Stochastic depletion analysis across all major interceptor and strike inventories

2. **How do we achieve overwhelming cost-asymmetry deterrence?**
   — CAR matrix ranks every threat/defender pairing from worst to best exchange ratio

3. **Where should the next marginal defence dollar go?**
   — Coverage-days-per-dollar ranking identifies highest readiness ROI

All data is drawn from **publicly available U.S. government sources** — CRS reports,
CSIS Missile Defense Project, DoD Selected Acquisition Reports, CENTCOM press releases,
and DoD budget documents. No classified data is used or required.

---

## Installation

```bash
git clone https://github.com/rjgreenresearch/cost-asymmetry-simulator
cd cost-asymmetry-simulator
pip install -r requirements.txt
```

**Python 3.10+ required.** Dependencies: `numpy`, `pyyaml`, `jinja2`, `matplotlib`, `fpdf2`.

> **Windows note:** After `pip install`, use `python -m pytest`  (always use `python -m pytest` on Windows) rather than `pytest`
> directly. On Windows, `pytest` may not be on the system PATH even after installation.
> `python -m pytest`  (always use `python -m pytest` on Windows) always works regardless of PATH configuration.

---

## Quick start

```bash
# Run with all defaults (90-day two-war horizon, $1B portfolio budget)
python -m cas

# List all configured weapon and threat systems
python -m cas --list-systems

# Custom run: 5,000 simulations, 60-day horizon, HTML+PDF report
python -m cas --n-sims 5000 --horizon 60 --report html,pdf

# Optimise a $5B portfolio with production surge
python -m cas --budget 5.0 --surge 0.5 --scenario two_war_surge

# Use a custom weapon systems database
python -m cas --weapon-config my_updated_weapons.yaml
```

All output is written to `output/<run_id>/` with datetime stamping:
```
output/
└── run_20260428_143022/
    ├── cas.log           ← full debug log (always written)
    ├── results.json      ← all simulation results (always written)
    ├── report.html       ← self-contained interactive report
    ├── report.pdf        ← print-ready report (if --report pdf)
    ├── car_matrix.csv    ← CAR table (if --report csv)
    ├── depletion.csv
    ├── marginal.csv
    └── run_manifest.json ← run metadata
```

> **Finding your log file:** the log is always at `output\<run_id>\cas.log`.
> The `<run_id>` is printed to the console at the start of every run:
> `INFO  CAS v1.1.0 | run_id=run_20260429_151311`
> The file log captures DEBUG-level detail; the console shows INFO and above.
> Use `--log-level DEBUG` to also see DEBUG output on the console.
> Use `--output-dir` to change the base output folder.

**Running the simulator — common commands:**
```bash
# Standard run (default 10,000 sims, 90-day horizon, $1B budget, HTML report)
python -m cas

# Quick test run (500 sims — fast, lower precision)
python -m cas --n-sims 500

# Full publication run (50,000 sims — slow, high precision)
python -m cas --n-sims 50000 --report html,pdf,json,csv

# List all weapon and threat systems, then exit
python -m cas --list-systems

# Custom budget and horizon
python -m cas --budget 5.0 --horizon 60

# Named scenario from simulation.yaml
python -m cas --scenario two_war_surge

# Debug mode — verbose console output
python -m cas --n-sims 500 --log-level DEBUG

# Custom weapon database
python -m cas --weapon-config my_weapons.yaml
```

---

## Command-line reference

```
python -m cas --help
```

| Flag | Default | Description |
|------|---------|-------------|
| `--n-sims N` | 10,000 | Monte Carlo iterations per system |
| `--horizon DAYS` | 90 | Simulation horizon (two-war standard = 90) |
| `--budget B` | 1.0 | Portfolio budget in $B |
| `--scenario NAME` | — | Named scenario from `simulation.yaml` |
| `--surge F` | 0.0 | Production surge fraction (0.5 = +50%) |
| `--weapon-config PATH` | config/ | Custom weapon systems YAML |
| `--threat-config PATH` | config/ | Custom threat systems YAML |
| `--sim-config PATH` | config/ | Custom simulation parameters YAML |
| `--output-dir DIR` | output/ | Base output directory |
| `--report FORMATS` | html | Comma-separated: html, pdf, json, csv, none |
| `--run-id ID` | auto | Override auto-generated run ID |
| `--log-level LEVEL` | INFO | Console log verbosity |
| `--list-systems` | — | Print all systems and exit |
| `--version` | — | Print version and exit |

---

## Configuration

All simulation parameters, weapon systems, and threat systems are defined in
human-readable YAML files under `config/`. No code changes are required to
add new systems or update cost data.

### `config/weapon_systems.yaml`

Each system entry includes:
- Unit cost, inventory estimate, production rates
- Quality tier and dud rate (for quality-adjusted CAR)
- Theater consumption rates (mean + coefficient of variation)
- Source citations for all cost figures

Example — adding a new system:
```yaml
systems:
  My_New_System:
    display_name: "New Interceptor XYZ"
    tier: OPERATIONAL
    type: interceptor_tactical
    unit_cost: 5000000
    inventory_est: 500
    annual_production: 200
    quality_tier: HIGH
    dud_rate: 0.02
    consumption_rates:
      theater_1: {mean: 10, cv: 0.4}
      theater_2: {mean: 8,  cv: 0.4}
    notes: "Source: CRS report XYZ"
    sources: ["CRS XYZ 2026"]
```

### `config/simulation.yaml`

Controls simulation parameters, scenario definitions, logging verbosity,
and output format defaults. Named scenarios can be invoked with `--scenario`.

### `config/threat_systems.yaml`

Adversary weapon system cost and capability data, including dud rates
(Russian Geran-2/Shahed: ~25% observed; Iranian MRBM: ~5%).

---

## Methodology

### Cost Asymmetry Ratio (CAR)
```
CAR = adversary unit cost / US defensive response cost
CAR_adj = (adversary effective cost) / (US effective cost)
        where effective cost = unit cost / (1 − dud_rate)
```
CAR < 1: adversary has cost advantage. CAR > 1: US has cost advantage.

### Monte Carlo demand model
Daily consumption sampled from **Negative Binomial(r, p)** calibrated from
mean and CV per theater. Negative Binomial is preferred over Poisson because
combat demand is overdispersed ("bursty") relative to a Poisson process.

Inter-theater correlation applied: when Theater 1 demand surges, Theater 2
mean is proportionally adjusted (correlation coefficient: 0.35).

### Dyna-METRIC adaptation
Adapted from the **Dyna-METRIC readiness-based sparing model**
(Sherbrooke 1968; RAND R-1872-AF), originally developed for aircraft spare
parts, here applied to consumable munitions. Key adaptation: consumable
systems deplete to zero (unlike repairable parts that cycle through repair).

The portfolio optimiser uses a **greedy marginal-value algorithm**: at each
$100M step, budget is allocated to the system with the highest marginal gain
in median days-of-coverage. This is tractable, transparent, and consistent
with the Dyna-METRIC sparing philosophy.

---

## Project structure

```
cost-asymmetry-simulator/
├── cas/
│   ├── __init__.py          # Package metadata
│   ├── __main__.py          # python -m cas entry point
│   ├── cli.py               # argparse CLI with full help
│   ├── config.py            # YAML config loader and Config class
│   ├── logging_config.py    # Rotating file + console logging
│   ├── simulator.py         # Deterministic CAR/depletion/marginal
│   ├── mc_simulator.py      # Monte Carlo engine (Dyna-METRIC)
│   ├── reporter.py          # HTML + PDF report generator
│   └── utils.py             # Run ID, file helpers, manifest
│
├── config/
│   ├── weapon_systems.yaml  # Weapon system database (editable)
│   ├── threat_systems.yaml  # Threat system database (editable)
│   └── simulation.yaml      # Simulation parameters and scenarios
│
├── templates/
│   └── report.html          # Jinja2 HTML report template
│
├── tests/
│   ├── test_config.py
│   ├── test_simulator.py
│   └── test_mc.py
│
├── docs/
│   └── methodology.md
│
├── output/                  # Created at runtime; gitignored
├── README.md
├── requirements.txt
├── setup.py
├── CITATION.cff
└── .gitignore
```

---

## Academic context

This simulator is the computational companion to:

> Green, R.J. (2026). "The Cost Curve as Deterrent: Compound Warfare
> Economics, Saturation Dynamics, and the Structural Unaffordability of
> Great-Power Conflict." *International Security* (forthcoming).
> SSRN: forthcoming.

Part of the **Mutual Threshold Saturation (MTS)** research programme:

| Paper | Pillar | Journal |
|-------|--------|---------|
| Paper 4 — Supply Chain Dependencies | MTS-1 | *Risk Analysis* |
| Paper 5 — Human Capital Threshold   | MTS-2 | *Intelligence and National Security* |
| **Paper 6 — Cost Curve as Deterrent** | **MTS-3** | ***International Security*** |
| Paper 7 — Compound Economic Fragility | MTS-4 | *Journal of Post Keynesian Economics* |
| Paper 8 — Aquifer Depletion          | MTS-5 | *Ecological Economics* |

---

## Data sources

All cost and inventory data is from publicly available U.S. government and
think-tank sources. Per-system citations are in `config/weapon_systems.yaml`.

Primary sources used:
- Congressional Research Service (CRS) reports IF12645, IF12611, RL30563
- CSIS Missile Defense Project interceptor cost database
- DoD Selected Acquisition Reports (SARs), FY2025/FY2026
- Missile Defense Agency (MDA) budget exhibits (P-21)
- CENTCOM press releases and briefings
- JINSA: "Missile and Interceptor Cost Estimates During the U.S.-Israel-Iran War" (2025)
- AEI: "Build Your Own Golden Dome" (September 2025)
- Norskluftvern Air Defense Systems Cost Database (March 2026)
- Brown University Costs of War Project

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## Citation

```bibtex
@software{green2026cas,
  author  = {Green, Robert J.},
  title   = {Cost-Asymmetry Simulator (CAS)},
  year    = {2026},
  version = {1.1.0},
  url     = {https://github.com/rjgreenresearch/cost-asymmetry-simulator},
  note    = {Companion software for Paper 6: The Cost Curve as Deterrent}
}
```

See also [CITATION.cff](CITATION.cff) for full citation metadata.

---

*Robert J. Green | rjgreenresearch.org | ORCID: 0009-0002-9097-1021*
