# Cost-Asymmetry Simulator (CAS) v1.1.0

Monte Carlo inventory optimisation engine for U.S. weapons systems under
two-war stochastic demand. Adapts the Dyna-METRIC readiness-based sparing
model (Sherbrooke 1968) to consumable munitions.

## Key Findings — Canonical Run

**Run:** `run_20260430_160009` | **N =** 10,000 | **Seed =** 20260428  
**Database:** 37 weapon systems | 12 threat systems | 90-day two-war horizon

### Depletion Results

| Category | Systems | Days to Zero |
|----------|---------|--------------|
| SELF-SUSTAINING | DroneHunter, STING, DroneRound 556, P1-Sun, Merops AS-3 | ∞ |
| MEDIUM RISK | APKWS (229d), SDB GBU-39 (215d), HIMARS GMLRS (298d), Hellfire (324d), Excalibur (139d) | 139–324 days |
| CRITICAL | JASSM-ER (80.7d), SM-2 (60.7d), Tomahawk (62.5d), PAC-3 MSE (46.8d), THAAD (37.3d) | 30–90 days |
| ACUTE CRISIS | SM-3 IIA (15.1d), LRASM (26.9d), Coyote (13.1d), Arrow-3 (16.9d) | < 30 days |

**Structural finding:** No U.S. interceptor system meets the 90-day two-war
planning standard at current inventories and production rates.

### Monte Carlo Readiness (P-coverage at Day 90)

All high-end interceptors: **P = 0.00%**  
JASSM-ER: **P = 0.08%** (8 survival cases per 10,000 — not operational readiness)  
DroneRound 556 NATO: **P = 96.96%**  
DroneHunter / STING / P1-Sun / Merops AS-3: **P = 100.00%** (self-sustaining)

### CAR Matrix (Representative 14 Pairings)

| Pairing | CAR | Status |
|---------|-----|--------|
| FPV drone vs. THAAD | 0.000 | ADV advantage |
| FPV drone vs. Patriot | 0.000135 | ADV advantage |
| Shahed vs. Patriot | 0.0054 | ADV advantage |
| MRBM vs. SM-3 IIA | 0.125 | ADV advantage |
| MRBM vs. THAAD | 0.236 | ADV advantage |
| FPV drone vs. DroneHunter (STING) | 0.200 | ADV advantage |
| ASBM vs. SM-6 | 1.163 | US advantage |
| Shahed vs. DroneHunter (STING) | **8.000** | US advantage |
| FPV vs. Iron Beam | 250 | US advantage |
| Shahed vs. Iron Beam | 10,000 | US advantage |

**Note:** DroneHunter cost corrected to $2,500 (STING baseline, Ukraine combat-proven).
Previous figure of $15,000 reflected U.S. DIU procurement estimates for Dedrone/Skydio.
See docs/DATA_SOURCES.md for full correction notice.

### Optimal $1B Portfolio Allocation

Greedy Dyna-METRIC algorithm, configurable tier caps:

| System | Tier | Allocated | Median Days |
|--------|------|-----------|-------------|
| Iron Dome Tamir | Allied Interceptor | $200M | 144 days |
| SDB GBU-39 | Precision Strike | $200M | 279 days |
| Coyote Block 3 | Attrition Defense | $200M | 72 days |
| Altius-600 | Attrition Offense | $200M | 230 days |
| DroneRound 762 | Infantry CUAS | $100M | 365 days |
| Excalibur M982 | Precision Strike | $100M | 160 days |
| **THAAD** | Strategic | **$0** | — |
| **SM-3 IIA** | Strategic | **$0** | — |
| **SM-2** | Operational | **$0** | — |

Zero allocation to THAAD, SM-3 IIA, SM-2, or SM-6 in optimal marginal portfolio.

### Marginal Value Ranking (Coverage-Days per $1B)

| System | Unit Cost | Days/$1B |
|--------|-----------|----------|
| DroneHunter (STING) | $2,500 | ∞ |
| DroneRound 556 | $8 | ∞ |
| P1-Sun / Merops AS-3 | $3,000–$3,500 | ∞ |
| DroneRound 762 | $12 | 640 |
| Altius-600 | $50,000 | 91.8 |
| Iron Dome Tamir | $50,000 | 47.9 |
| SDB GBU-39 | $40,000 | 31.6 |
| ... | ... | ... |
| THAAD | $12,700,000 | 7.9 |
| SM-3 IIA | $24,000,000 | 3.7 |

**1,730-fold spread** between SM-3 IIA (3.7 days/$1B) and DroneRound 762 (6,404 days/$1B).

## Quick Start

```bash
pip install -e .
python -m cas --n-sims 10000 --report html,json
```

To reproduce canonical results:
```bash
python -m cas --n-sims 10000 --report html,json
# run_id: run_20260430_160009 | seed: 20260428
```

## Database

- `config/weapon_systems.yaml` — 37 systems across 9 tiers
- `config/threat_systems.yaml` — 12 adversary systems
- `config/simulation.yaml` — Monte Carlo parameters and portfolio caps
- `docs/DATA_SOURCES.md` — per-system source citations

## Methodology

- **Demand model:** Negative Binomial (overdispersed; CV = 0.35–0.80 per system)
- **Inter-theater correlation:** θ = 0.35 (Middle East + Indo-Pacific)
- **Portfolio optimisation:** Greedy marginal-value algorithm with configurable tier caps
- **Readiness metric:** P(inventory > 0 at day 90) — days-of-coverage

## Citation

Green, R.J. (2026). *The Cost Curve as Deterrent: Compound Warfare Economics,
Saturation Dynamics, and the Structural Unaffordability of Great-Power Conflict.*
SSRN Working Paper. Submitted to Defence and Peace Economics.
github.com/rjgreenresearch/cost-asymmetry-simulator

## License

Apache 2.0 — see LICENSE
