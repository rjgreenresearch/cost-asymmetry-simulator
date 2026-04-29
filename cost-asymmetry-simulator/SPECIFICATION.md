# Cost Asymmetry Simulator — Technical Specification
## Compound Warfare Economics Modeling Tool
### Companion Software for Paper 6

**Version:** 0.1 (Specification)
**Author:** Robert J. Green
**Relationship to existing tools:** Third tool in the MTS suite. Shares mts-core library with mts-doctrine-simulator (supply chains) and hcts-simulator (human capital). Models cost-exchange dynamics, attrition trajectories, and compound deterrence across warfare domains.

---

## 1. Architecture

```
mts-core/                         # Shared library
├── graph/                        # Network topology
├── indices/                      # HHI, HCDI, CAR metrics
├── simulation/                   # Monte Carlo engine
└── export/                       # CSV, JSON, visualization

mts-doctrine-simulator/           # Paper 4 (existing, 98 tests)
hcts-simulator/                   # Paper 5 (specified)
cost-asymmetry-simulator/         # Paper 6 (this spec)
├── imports mts-core
├── cost_models/
│   ├── offense_defense.py        # CAR computation per system pair
│   ├── attrition_replacement.py  # Platform loss/replacement modeling
│   ├── industrial_tempo.py       # Production cycle comparison
│   ├── economic_cascade.py       # Cross-sector disruption costs
│   └── reconstruction.py         # Post-conflict fiscal burden
├── scenarios/
│   ├── epic_fury.py              # Houthi Red Sea cost-exchange
│   ├── taiwan_strait.py          # Compound cost across all 5 domains
│   ├── hormuz_closure.py         # Economic cascade modeling
│   └── drone_saturation.py       # OWA vs interceptor dynamics
├── compound/
│   ├── three_pillar.py           # Material + Human Capital + Cost
│   └── deterrence_threshold.py   # Compound deterrence assessment
└── tests/                        # 100+ automated tests
```

---

## 2. Core Data Model

### 2.1 Weapon System Node

```python
@dataclass
class WeaponSystem:
    id: str
    name: str
    category: Category           # OFFENSIVE | DEFENSIVE | DUAL_USE
    
    # Cost attributes
    unit_cost_usd: float         # Per-unit procurement cost
    marginal_engagement_cost: float  # Cost per engagement/shot
    annual_operating_cost: float # Sustainment per unit per year
    
    # Production attributes
    production_time_months: float # Time to produce one unit
    max_monthly_production: int  # Industrial surge capacity
    supply_chain_dependencies: list[str]  # MTS dependency IDs
    
    # Performance attributes
    engagement_probability: float  # P(kill) per engagement
    magazine_depth: int          # Engagements before reload/resupply
    sortie_rate: float           # Engagements per day
    
    # Survivability
    platform_survivability: float  # P(survive) per engagement cycle
    replacement_time_months: float # Time to replace if destroyed
```

### 2.2 Cost Asymmetry Ratio

```python
@dataclass
class CostAsymmetryRatio:
    offensive_system: str
    defensive_system: str
    car: float                   # Cost ratio (offense/defense)
    scale_factor: float          # At what production scale CAR applies
    
    # Computed fields
    defender_budget_exhaustion: float  # Engagements until defender bankrupt
    attacker_budget_exhaustion: float  # Engagements until attacker bankrupt
    crossover_point: int         # Engagement count where advantage shifts
```

### 2.3 Conflict Scenario

```python
@dataclass
class ConflictScenario:
    name: str
    duration_days: int
    
    # Force structure
    blue_systems: list[WeaponSystem]
    red_systems: list[WeaponSystem]
    
    # Economic context
    blue_gdp: float
    red_gdp: float
    blue_defense_budget: float
    red_defense_budget: float
    
    # Supply chain context (links to mts-doctrine-simulator)
    supply_chain_disruptions: list[str]  # MTS dependency IDs affected
    
    # Human capital context (links to hcts-simulator)
    personnel_attrition: dict    # Function → attrition rate
```

---

## 3. Simulation Engines

### 3.1 Engagement Cost Exchange

```python
def simulate_engagement_exchange(
    offense: list[WeaponSystem],
    defense: list[WeaponSystem],
    attack_tempo: int,           # Offensive sorties per day
    duration_days: int,
    resupply_model: str = "realistic"
) -> ExchangeResult:
    """
    Simulate day-by-day cost exchange between offensive
    saturation and defensive interception.
    
    Tracks: cumulative costs, magazine depletion,
    platform attrition, industrial replacement queue.
    
    Returns daily cost trajectories and sustainability
    assessment for both sides.
    """
```

### 3.2 Compound Conflict Cost

```python
def simulate_compound_cost(
    scenario: ConflictScenario,
    material_model: SupplyChainModel,    # From mts-doctrine-simulator
    human_capital_model: HumanCapitalModel,  # From hcts-simulator
    time_horizon_years: int = 10
) -> CompoundCostResult:
    """
    Simulate the full compound cost of a conflict scenario
    across all five domains simultaneously.
    
    1. Direct military costs (engagement exchange)
    2. Platform replacement costs (attrition-replacement)
    3. Supply chain cascade costs (Material MTS integration)
    4. Human capital loss costs (HCTS integration)  
    5. Economic cascade costs (trade disruption)
    6. Reconstruction burden (post-conflict projection)
    
    Returns: Domain-by-domain and compound cost trajectories,
    cost-as-fraction-of-GDP over time, and deterrence
    threshold assessment.
    """
```

### 3.3 Deterrence Threshold Calculator

```python
def assess_deterrence(
    blue_scenario: CompoundCostResult,
    red_scenario: CompoundCostResult,
    blue_objectives: dict,       # Strategic gains if victorious
    red_objectives: dict
) -> DeterrenceAssessment:
    """
    Compare expected compound costs against expected
    strategic gains for both sides.
    
    Deterrence obtains when:
    - Expected cost > Expected gain for BOTH sides
    - Cost visibility is sufficient for rational calculation
    - No first-mover advantage eliminates the cost asymmetry
    
    Returns: Deterrence stability score, domain-by-domain
    cost-gain comparison, and identification of the
    weakest deterrence pillar.
    """
```

---

## 4. Pre-Built Scenarios

### 4.1 Operation Epic Fury (Red Sea)
- Houthi OWA drones ($20K-$50K) vs SM-2/SM-6 ($2.1M-$4.3M)
- CAR ≈ 1:100
- Model interceptor inventory depletion rate
- Model Houthi resupply via Iranian logistics
- Assess sustainability horizon for both sides

### 4.2 Taiwan Strait Compound Scenario
- Integrate all five cost domains simultaneously
- Semiconductor disruption cascade (Material MTS)
- Naval platform attrition (carrier, submarine losses)
- Analyst/operator attrition (Human Capital MTS)
- Global trade disruption (economic cascade)
- Reconstruction projection (20-year horizon)

### 4.3 Drone Saturation Defense
- 30,000 OWA drones vs layered defense
- Model: interceptor-only defense cost trajectory
- Model: DEW-augmented defense cost trajectory
- Compare sustainability under each architecture

### 4.4 A-10 vs F-35 Cost-Exchange Comparison
- Close air support mission profile
- Operating cost per sortie
- Attrition risk per sortie
- Replacement timeline if lost
- Demonstrate cost-curve advantage of legacy modernization

---

## 5. Output Formats

- **Cost Exchange Dashboard**: Day-by-day cost trajectories for both sides
- **CAR Matrix**: System-vs-system cost asymmetry ratios
- **Compound Cost Projection**: Five-domain stacked cost chart over time
- **Deterrence Assessment**: Traffic-light indicator per domain and compound
- **Budget Sustainability**: Time-to-exhaustion under various scenarios
- **Industrial Tempo Comparison**: Production rate vs attrition rate charts
- **Export**: CSV cost ledger, JSON for programmatic consumption

---

## 6. Testing Requirements

Target: 100+ automated tests

| Category | Tests | Description |
|----------|-------|-------------|
| Data model | 15 | WeaponSystem validation, CAR computation |
| Engagement exchange | 20 | Day-by-day simulation, magazine depletion, resupply |
| Compound cost | 20 | Five-domain integration, multiplicative cascades |
| Deterrence threshold | 15 | Cost-gain comparison, stability assessment |
| Scenarios | 15 | Epic Fury, Taiwan, drone saturation, A-10 vs F-35 |
| Integration | 10 | mts-core, mts-doctrine-simulator, hcts-simulator |
| Export | 5 | CSV, JSON, visualization |

---

## 7. Technology Stack

- **Language:** Python 3.11+
- **Dependencies:** NumPy, NetworkX, Matplotlib, pytest
- **License:** Apache 2.0
- **Repository:** github.com/rjgreenresearch/cost-asymmetry-simulator
- **CI/CD:** GitHub Actions

---

## 8. Compound Deterrence Integration

The ultimate analytical capability is the three-pillar compound deterrence assessment:

```python
from mts_core.compound import ThreePillarAssessment
from mts_doctrine_simulator import SupplyChainModel
from hcts_simulator import HumanCapitalModel
from cost_asymmetry_simulator import ConflictModel

assessment = ThreePillarAssessment(
    material=SupplyChainModel.load("taiwan_semiconductor_disruption"),
    human_capital=HumanCapitalModel.load("indo_pacific_analyst_attrition"),
    cost=ConflictModel.load("taiwan_strait_compound"),
    blue_objectives={"semiconductor_security": 5e12},  # $5T strategic value
    red_objectives={"reunification": 3e12}              # $3T strategic value
)

result = assessment.evaluate()
# Returns: compound deterrence score, weakest pillar,
# domain-by-domain cost-gain ratios, stability assessment
```

This integration demonstrates the complete MTS architecture: no single pillar is sufficient for deterrence, but the compound of all three creates the structural unaffordability that the paper theorizes.
