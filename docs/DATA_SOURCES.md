# Data Sources
## Cost-Asymmetry Simulator (CAS) — MTS Pillar 3

All cost, inventory, consumption rate, and engagement data used in this simulator
is drawn exclusively from **publicly available sources**. No classified data is used
or required. Sources are organised by category and cross-referenced to the
specific variables they inform in `config/weapon_systems.yaml` and
`config/threat_systems.yaml`.

---

## Table of Contents

1. [Congressional Research Service (CRS)](#1-congressional-research-service-crs)
2. [DoD Selected Acquisition Reports (SARs)](#2-dod-selected-acquisition-reports-sars)
3. [Missile Defense Agency (MDA) Budget Exhibits](#3-missile-defense-agency-mda-budget-exhibits)
4. [CSIS Missile Defense Project](#4-csis-missile-defense-project)
5. [JINSA Cost Estimates](#5-jinsa-israel-iran-war-cost-estimates)
6. [AEI Golden Dome Working Paper](#6-aei-working-paper)
7. [CENTCOM Press Releases and Briefings](#7-centcom-press-releases-and-briefings)
8. [Norskluftvern Air Defense Database](#8-norskluftvern-air-defense-cost-database)
9. [DoD Budget Documents](#9-dod-budget-documents)
10. [Industry Sources](#10-industry-sources)
11. [Think-Tank and Academic Sources](#11-think-tank-and-academic-sources)
12. [Ukraine Conflict OSINT](#12-ukraine-conflict-open-source-intelligence)
13. [IISS Military Balance](#13-iiss-military-balance)
14. [Methodology Foundations](#14-methodology-foundations)
15. [Variables-to-Sources Cross-Reference](#15-variables-to-sources-cross-reference)
16. [Limitations and Uncertainty Disclosures](#16-limitations-and-uncertainty-disclosures)

---

## 1. Congressional Research Service (CRS)

CRS reports are produced by the nonpartisan research arm of the U.S. Congress
and are the primary authoritative source for U.S. weapons system procurement
costs, production rates, and inventory context. All reports are publicly
available through the Federation of American Scientists (fas.org/sgp/crs) or
directly from congress.gov.

| Report | Title | Key Variables Informed |
|--------|-------|----------------------|
| **IF12645** | The Terminal High Altitude Area Defense (THAAD) System | THAAD unit cost, battery cost, production rate, inventory context |
| **RL33745** | Navy Aegis Ballistic Missile Defense (BMD) Program | SM-3 IIA unit cost trajectory, production ceiling, SM-2/SM-6 context |
| **R45811** | Hypersonic Weapons: Background and Issues for Congress | DF-17 threat characterisation, GPI gap, intercept impossibility |
| **IF12611** | The Switchblade Loitering Munition | Switchblade 600 unit cost (~$100K), Replicator programme inclusion |
| **RL30563** | Tomahawk Cruise Missile | Tomahawk unit cost ($2.1M), production rate (350/yr), inventory context |
| **IF10541** | U.S. Ballistic Missile Defense | System overview, THAAD/SM-3 programmatic context |
| **RL33240** | Kinetic Energy Kill for Ballistic Missile Defense | Patriot/PAC-3 historical cost trajectory |
| **RS22595** | Navy Aegis Cruiser and Destroyer Modernization | Aegis platform SM-6 deployment context |

**Primary access:** https://sgp.fas.org/crs/ and https://crsreports.congress.gov

---

## 2. DoD Selected Acquisition Reports (SARs)

SARs are annual cost and schedule reports submitted by major defense acquisition
programmes to Congress under 10 U.S.C. § 2432. They are the most authoritative
public source for unit costs, total programme value, and schedule status.
Released annually; most recent editions used are FY2025.

| Programme | System | Key Data Points |
|-----------|--------|-----------------|
| THAAD SAR | THAAD interceptor | Unit recurring flyaway cost; programme total; schedule |
| Standard Missile-3 SAR | SM-3 Block IIA | Unit cost history FY2021–FY2025 ($9M → $24M trajectory) |
| Standard Missile-6 SAR | SM-6 | Unit cost ($4.3M), production quantities |
| Standard Missile-2 SAR | SM-2 | Unit cost ($2M), ageing fleet status |
| Tomahawk SAR | TLAM Block IV/V | Unit cost ($2.1M), annual production, total programme |
| JASSM-ER SAR | JASSM-ER | Unit cost ($1.5M), production ramp, inventory estimate |

**Access:** SARs are submitted to the House and Senate Armed Services Committees
and released publicly via the Pentagon Comptroller website and through FOIA.
Historical SARs available at: https://www.esd.whs.mil/Portals/54/Documents/

---

## 3. Missile Defense Agency (MDA) Budget Exhibits

MDA submits detailed programme budget justification documents (P-21 exhibits)
with each President's Budget request. These contain the most granular public
cost data for missile defense programmes including unit cost by lot, production
quantities, and multi-year procurement plans.

| Document | Key Data Points |
|----------|-----------------|
| MDA P-21 FY2025 Budget Exhibits | THAAD unit cost ($12.7M), SM-3 IIA production pause/restart, interceptor lot pricing |
| MDA P-21 FY2026 Budget Exhibits | THAAD production ramp to 57 units ($840M request), SM-3 cost escalation |
| MDA P-21 FY2027 Budget Exhibits | Drone Autonomous Warfare Group (DAWG) $54.6B request context |

**Access:** https://comptroller.defense.gov/Budget-Materials/ under the
respective fiscal year's RDT&E and Procurement budget justification documents.

---

## 4. CSIS Missile Defense Project

The Center for Strategic and International Studies Missile Defense Project
maintains the most comprehensive public database of interceptor costs, threat
system costs, and engagement history. It is the primary independent cross-check
for MDA and SAR data.

| Publication | Key Data Points |
|-------------|-----------------|
| CSIS Missile Defense Project: Missile Threat | THAAD, SM-3, PAC-3 unit costs and intercept rates; Iranian MRBM threat characterisation |
| CSIS China Power Project | DF-17 hypersonic glide vehicle specifications and cost estimates; DF-21D/DF-26 ASBM data |
| CSIS Iran Missile Threat Assessment | Iranian ballistic missile inventory, unit cost estimates, production capacity |
| "Evaluating U.S. Missile Defense Programs" | Two-war inventory adequacy analysis; production rate benchmarks |

**Primary access:** https://missilethreat.csis.org/ and https://chinapower.csis.org/

**Specific cost data used:**
- PAC-3 MSE unit cost: $3.7M (CSIS cross-referenced with JINSA 2025)
- SM-3 IIA cost trajectory: $9M (FY2021) → $24M (FY2024) documented in CSIS programme tracker
- THAAD intercept rate vs. MRBMs: 90% (CSIS operational assessment)

---

## 5. JINSA Israel-Iran War Cost Estimates

The Jewish Institute for National Security of America published a detailed
post-engagement cost analysis of the U.S. missile expenditures during the
Israel-Iran conflict of 2025 and Operation Epic Fury (February–March 2026).
This is the primary source for engagement-specific cost and consumption data.

| Publication | Key Data Points |
|-------------|-----------------|
| JINSA, "Missile and Interceptor Cost Estimates During the U.S.-Israel-Iran War" (2025) | Per-system unit costs cross-referenced against SAR data; engagement-specific consumption; THAAD pre-/post-conflict inventory estimates; PAC-3 MSE $3.7M confirmation |

**Specific data points sourced from JINSA:**
- THAAD inventory estimate: ~632 pre-2025 conflict, ~370 post-Epic Fury
- PAC-3 MSE: $3.7M/unit (confirmed independently of SAR)
- SM-2/SM-6 engagement rates: approximately 30/day and 8/day respectively
  at high-intensity sustained operations

---

## 6. AEI Working Paper

| Publication | Key Data Points |
|-------------|-----------------|
| American Enterprise Institute, "Build Your Own Golden Dome: A Constructive Proposal for the United States to Achieve Cost-Effective Missile Defense" (September 2025) | THAAD battery cost ($2.73B per battery including 192 interceptors); production economics; directed energy cost comparison |

**Specific data points sourced:**
- THAAD battery cost: $2.73B (8 launchers, 192 interceptors, AN/TPY-2 radar, C2)
- Cost-per-intercept analysis for THAAD vs. lower-tier systems
- Directed energy as cost-curve inflection argument

---

## 7. CENTCOM Press Releases and Briefings

U.S. Central Command official press releases and background briefings are the
primary source for Operation Epic Fury engagement statistics and the LUCAS
drone programme confirmation.

| Document | Key Data Points |
|----------|-----------------|
| CENTCOM Statement, March 2, 2026 | LUCAS (FLM-136) unit cost confirmed at $35,000; first combat use February 28, 2026; SpektreWorks AZ manufacturer |
| CENTCOM Operation Epic Fury press releases (February–March 2026) | Engagement statistics: Iranian ballistic missile sortie rates; interceptor consumption by system type; operational tempo |
| CENTCOM Background Briefings (2025–2026) | FPV drone threat characterisation by Iranian proxies; $500 unit cost range confirmed |

**Primary access:** https://www.centcom.mil/MEDIA/PRESS-RELEASES/

---

## 8. Norskluftvern Air Defense Cost Database

Norskluftvern (Norwegian Air Defence) maintains an independent open-source
database of global air defense systems with cost-per-engagement analysis,
updated based on publicly available data and manufacturer specifications.

| Publication | Key Data Points |
|-------------|-----------------|
| Norskluftvern Air Defense Systems Cost Database (March 2026 update) | Iron Beam DEW: per-shot cost ~$2 (laser electricity at Israeli grid prices); HELIOS per-shot cost ~$1; system capital cost estimates; operational confirmation Lebanon 2026 |

**Specific data points:**
- Iron Beam per-shot cost: ~$2 (confirmed vs. Elbit/Rafael published power consumption specs and Israeli industrial electricity rates)
- Iron Beam operational confirmation: intercept of drones and rockets in Lebanon, March 2026
- System capital cost: ~$20M per unit (manufacturer-stated range)

**Access:** https://www.norskluftvern.com/

---

## 9. DoD Budget Documents

| Document | Key Data Points |
|----------|-----------------|
| FY2027 President's Budget Request, DoD | Drone Autonomous Warfare Group (DAWG): $54.6B request (24,000% increase vs. FY2026 $225M); total drone/C-UAS request >$70B |
| FY2026 DoD Budget: Procurement Appendix | LUCAS Drone Dominance Programme: 300,000-unit target; Phase IV unit cost target $5,000 |
| FY2026 Navy Procurement: P-40 Exhibit | HELIOS programme: $150M per system; USS Preble operational at 60kW |
| FY2026 Army Procurement: P-40 Exhibit | PAC-3 MSE: Lockheed Martin ramp to 650/yr (announced); 2,000/yr FY2027 target |

**Access:** https://comptroller.defense.gov/Budget-Materials/

---

## 10. Industry Sources

| Source | Key Data Points |
|--------|-----------------|
| Lockheed Martin Investor Briefings (2025) | PAC-3 MSE: 500/yr current production; ramp to 650/yr; Aegis Combat System SM-6 production context |
| Lockheed Martin HELIOS Programme Brief | HELIOS: $150M/system; 60kW operational; 150kW scalable; USS Preble deployment |
| dsm.forecastinternational.com (December 2025) | LUCAS drone cost history; Drone Dominance vendor pool (20 vendors); unit economics at scale |
| drone-warfare.com (March 2026) | LUCAS first combat deployment details; SpektreWorks production capacity; $35K/unit confirmation |

---

## 11. Think-Tank and Academic Sources

| Source | Key Data Points |
|--------|-----------------|
| RAND Corporation, "Sustaining the Fight: Resilient Maritime Logistics for a Complex Conflict" | Two-war consumption rate benchmarks for strike weapons; Tomahawk and JASSM-ER utilisation rates under sustained high-intensity operations |
| RAND R-1872-AF, Sherbrooke (1968) | Dyna-METRIC readiness-based sparing model — methodological foundation for the Monte Carlo inventory engine |
| Brown University Costs of War Project | Aggregate weapons expenditure context; cost-per-engagement historical data |
| Responsible Statecraft (2025) | Switchblade 600: unit cost ($100K estimated), Replicator programme inclusion, inventory status |
| IISS Military Balance 2025 | Adversary system costs: Shahed-136 ($20K), Iranian MRBM ($3M estimated), DF-17 ($10M estimated); order-of-battle context |

---

## 12. Ukraine Conflict Open-Source Intelligence

Ukraine battlefield data is used for three specific variables: Shahed-136 and
Geran-2 failure/dud rates, FPV drone tactical cost ranges, and DroneHunter
effectiveness estimates. All data is from open-source aggregators and has been
cross-checked against multiple independent sources.

| Source | Key Data Points |
|--------|-----------------|
| Ukraine battlefield OSINT (2023–2026) — aggregated via Oryx, DeepState Map, Ukraine MoD releases | Shahed-136 / Geran-2: 20–35% observed failure rate (dud rate 0.25 used); total launches vs. intercepts vs. failures tracked |
| DIU (Defense Innovation Unit) C-UAS briefings (2025–2026) | DroneHunter intercept effectiveness: ~70% vs. Group 1/2 UAS; tactical deployment doctrine; $15K unit cost range |
| DIU Replicator Programme briefings (2025–2026) | FPV quadcopter cost range ($400–$2,000); Group 1 UAS doctrine; mass-production quality risks |

**CORRECTION — DroneHunter unit cost (updated April 2026):**
The original $15,000 unit cost figure for DroneHunter was sourced from U.S. DIU
procurement estimates for Dedrone and Skydio platforms. Primary-source research
identifies three Ukrainian combat-proven drone-hunting systems at materially
lower costs:

- **STING** (Wild Hornets): ~$2,500. FPV collision intercept. 25km range. 1,000+
  Shahed kills in first four months. 360° antenna, EW-resistant, night-capable.
- **General Cherry interceptors**: $1,000–$2,275. ~1,000/day production rate.
- **P1-Sun / Merops AS-3**: Air-launched variants; cost not publicly stated.
  Used by U.S. forces in Middle East (CENTCOM 2025–2026).

The simulator's DroneHunter entry has been corrected to $2,500 (STING baseline).
This changes the Shahed-vs-DroneHunter CAR from 1.33 to **8.0** — shifting the
pairing from US_ADVANTAGE to a significantly stronger US_ADVANTAGE. The FPV-vs-
DroneHunter CAR improves from 0.033 to **0.20** — still adversary advantage but
six times more favorable than the previous estimate. DroneHunter now appears at
the top of the marginal value ranking alongside DroneRound 556 at ∞ days/$100M.

**Critical caveat on dud rate data:** The 20–35% Shahed failure rate is derived
from Ukrainian MoD and independent OSINT tracking and reflects the entire failure
mode spectrum (navigation failure, structural failure, Ukrainian electronic warfare,
and soft intercept). It is used as evidence for the **quality discipline argument**
only — the simulator does not claim this rate applies to any U.S. system.

---

## 13. IISS Military Balance

| Publication | Key Data Points |
|-------------|-----------------|
| International Institute for Strategic Studies, *The Military Balance 2025* (Routledge, 2025) | Iranian MRBM inventory size and composition; Shahed-136 production capacity; Chinese DF-17 programme status; ASBM DF-21D/DF-26 operational inventory; Russian Geran-2 deployment numbers |

**Specific data used:**
- Iranian ballistic missile production estimate: ~500 missiles produced FY2025–FY2026
  (cross-referenced with CENTCOM estimates)
- Shahed-136 unit cost: $20,000 (IISS estimate, corroborated by Ukrainian MoD)

---

## 14. Methodology Foundations

The Monte Carlo demand model and portfolio optimisation algorithm are adapted
from the following published academic and government research:

| Source | Role in Simulator |
|--------|-------------------|
| Sherbrooke, C.C. (1968). "METRIC: A Multi-Echelon Technique for Recoverable Item Control." *Operations Research*, 16(1), 122–141. | Foundational Dyna-METRIC model architecture |
| Hildebrandt, G., and Sze, M. (1990). "An Improved Dyna-METRIC Model." RAND R-3837-AF. | Extended Dyna-METRIC with multi-indenture structure |
| Slay, F.M., et al. (1996). "Optimizing Spares Support: The Aircraft Sustainability Model." RAND MR-686-AF. | Readiness-based sparing optimisation approach |
| Sherbrooke, C.C. (2004). *Optimal Inventory Modeling of Systems*. Kluwer. | Negative Binomial demand distribution for spare parts / consumables |

**Adaptation note:** Dyna-METRIC was designed for *repairable* aircraft spare parts
with a repair pipeline. CAS adapts it for *consumable* munitions where depleted
inventory is not recovered. The key adaptation is replacing the repair pipeline
with a production lag, and replacing fill rates with days-of-coverage as the
primary readiness metric.

---

## 15. Variables-to-Sources Cross-Reference

| Variable | System | Value Used | Primary Source | Confidence |
|----------|--------|------------|----------------|------------|
| Unit cost | THAAD | $12.7M | CRS IF12645; MDA P-21 FY2026 | HIGH |
| Inventory | THAAD | ~370 | JINSA 2025; CENTCOM (post-Epic Fury) | MEDIUM |
| Production | THAAD | 32/yr | MDA P-21 FY2026 budget request | HIGH |
| Unit cost | SM-3 IIA | $24M | MDA P-21 FY2025; CSIS | HIGH |
| Unit cost | PAC-3 MSE | $3.7M | JINSA 2025; CSIS | HIGH |
| Unit cost | SM-6 | $4.3M | SAR; CSIS | HIGH |
| Unit cost | Tomahawk | $2.1M | SAR; CRS RL30563 | HIGH |
| Unit cost | JASSM-ER | $1.5M | SAR; USAF budget | HIGH |
| Unit cost | LUCAS | $35K | CENTCOM March 2, 2026 | HIGH |
| Future cost | LUCAS | $5K | DoD FY2026 budget (Phase IV target) | MEDIUM |
| Unit cost | FPV drone | $800 | DIU; Ukraine OSINT (range $400–$2K) | MEDIUM |
| Unit cost | Switchblade 600 | $100K | CRS IF12611 (estimated) | MEDIUM |
| Unit cost | DroneHunter | $15K | DIU C-UAS briefings | MEDIUM |
| Per-shot cost | Iron Beam DEW | $2 | Norskluftvern March 2026 | MEDIUM |
| System cost | Iron Beam DEW | $20M | Elbit/Rafael statements; Norskluftvern | MEDIUM |
| System cost | HELIOS | $150M | Navy P-40; Lockheed briefings | HIGH |
| Unit cost | Shahed-136 | $20K | IISS MB 2025; Ukraine MoD | MEDIUM |
| Dud rate | Shahed/Geran-2 | 25% | Ukraine OSINT aggregated 2023–2026 | MEDIUM |
| Unit cost | Iranian MRBM | $3M | CSIS; IISS MB 2025 | LOW-MEDIUM |
| Unit cost | DF-17 | $10M | CSIS China Power | LOW |
| Unit cost | DF-21D/DF-26 | $5M | CSIS; RAND | LOW |
| Consumption T1 mean | THAAD | 7/day | JINSA 2025 engagement rate; CENTCOM | MEDIUM |
| Consumption T1 mean | Tomahawk | 25/day | RAND sustained ops estimates | MEDIUM |
| Consumption T1 mean | LUCAS | 500/day | CAS modelling assumption (no conflict data) | LOW |

**Confidence levels:** HIGH = confirmed in multiple independent government sources;
MEDIUM = single government or credible independent source; LOW = estimate with
significant uncertainty, used with explicit caveats in the simulator output.

---

## 16. Limitations and Uncertainty Disclosures

**Inventory figures are estimates.** Actual U.S. weapons inventories are
classified. All figures used are open-source estimates from CRS, CSIS, JINSA,
and post-engagement OSINT analysis. The THAAD figure of ~370 post-Epic Fury
is particularly uncertain; it is the CAS model's best open-source estimate
and should be treated as approximate.

**Consumption rates are modelled, not observed (for LUCAS/FPV).** The
LUCAS and FPV quadcopter consumption rates are modelling assumptions based
on the Drone Dominance Programme's stated doctrine, not from observed
conflict data for these specific U.S. systems. THAAD, SM-3, PAC-3, and
Tomahawk consumption rates are informed by JINSA engagement analysis from
the 2025 Israel-Iran conflict and the 2026 Epic Fury operation.

**Cost data ages.** Unit costs for all systems change with annual procurement
decisions, inflation adjustments, and lot-size changes. The SM-3 IIA cost
increase from $9M (FY2021) to $24M (FY2024) illustrates how rapidly costs
can escalate. All cost figures are documented by fiscal year in
`config/weapon_systems.yaml` and should be updated annually.

**Adversary cost estimates have high uncertainty.** Iranian MRBM and Chinese
DF-17 unit cost estimates are derived from IISS and CSIS analysis and carry
LOW confidence. They are used only for the CAR computation where the
US/adversary ratio, not the absolute value, is the policy-relevant output.
A factor-of-2 error in adversary costs shifts the CAR by a factor of 2 —
large in absolute terms but irrelevant when comparing a $500 FPV to a $3.7M
PAC-3 (7,400:1 CAR vs. 3,700:1 CAR at double the FPV cost).

**No classified data.** This simulator is designed for academic and policy
research and does not incorporate classified sources. DoD analysts with
access to classified inventory and consumption data will be able to produce
more accurate results by updating `config/weapon_systems.yaml` with
authoritative figures.

---

*Last updated: April 28, 2026 | CAS v1.1.0 | Robert J. Green*
*robert@rjgreenresearch.org | ORCID: 0009-0002-9097-1021*

---

## 17. Personal Drone Defense Munitions (Added April 2026)

Infantry-level anti-drone munitions represent the lowest-cost tier of the
C-UAS ecosystem. Three systems added to the simulator database in April 2026.

| Source | Systems | Key Data Points |
|--------|---------|-----------------|
| ALS / Maverick Tactical product data; Botach / Primary Arms retail pricing (2026) | Skynet_12GA_AntiDrone | Unit cost $46–48; 5 tethered projectiles; 5-foot net diameter; 12-gauge standard |
| Pew Pew Tactical, "Shotguns and Drones" (August 2025) | Skynet_12GA_AntiDrone | U.S. Air Force procurement confirmed; Ukraine battlefield effectiveness documentation |
| SHOT Show 2026 coverage, Sandboxx News (February 6, 2026) | All three | Market overview; system comparisons; Benelli M4 A.I. Drone Guardian platform |
| The Firearm Blog, SHOT Show 2026 coverage (January 30, 2026) | DroneRound_556_NATO, DroneRound_762_NATO | Velocity data (2,200 fps); effective ranges (50m K-variant, 100m L-variant); production capacity (350M rounds/yr); military/LE-only restriction |
| Drone Round Defense SHOT 2026 booth data | DroneRound_556_NATO, DroneRound_762_NATO | Projectile count per variant; STANAG magazine compatibility; no-modification deployment |

**Strategic note on CAR for personal drone defense:**
At $47/shell vs. a $500 FPV adversary drone, the Skynet round's CAR is
approximately 0.094 — meaning the adversary spent roughly 10× more to
deploy the threat than the defender spent to neutralise it. This is one
of the few favourable cost-exchange pairings for the defending force at
the tactical level, and it is available at scale immediately from
existing industrial capacity.

The 5.56 Drone Round at estimated $8/round vs. a $500 FPV drone yields
a CAR of approximately 0.016 — for every dollar of adversary expenditure,
the US defender spends roughly $0.016 at the infantry engagement level.
The $8 round fired from an M4 a soldier already carries requires no
additional logistics burden.

**Uncertainty note:** Unit costs for both systems are early-production
estimates. At the production volumes these companies are targeting (350M
rounds/yr for Drone Round Defense), unit economics will improve
significantly. The $6–12 range for 5.56 Drone Round should be
treated as an upper bound for near-term DoD procurement at scale.
