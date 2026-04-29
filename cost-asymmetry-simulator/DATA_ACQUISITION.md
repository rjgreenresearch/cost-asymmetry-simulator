# MTS Research Programme — Data Acquisition Guide
## Source Catalog, Collection Protocols, and Repository Organization
### Version 1.0 — April 2026

Robert J. Green | rjgreenresearch.org

---

## Purpose

This document catalogs every primary data source required for Papers 5 and 6 of the MTS research programme, specifies the collection protocol for each source, defines the repository file structure, and provides checklists to ensure completeness and reproducibility. It is designed to live in the repository root as DATA_ACQUISITION.md so that any researcher can replicate the data collection process.

---

## Repository Structure

```
mts-data/
├── DATA_ACQUISITION.md              # This document
├── README.md                        # Repository overview and citation
├── LICENSE                          # Apache 2.0
│
├── raw/                             # Unmodified source files as downloaded
│   ├── dod_budget/                  # DoD Comptroller J-Books, SARs
│   ├── crs_reports/                 # Congressional Research Service
│   ├── gao_reports/                 # Government Accountability Office
│   ├── centcom/                     # CENTCOM press releases and briefings
│   ├── odni/                        # ODNI workforce demographics
│   ├── opm/                         # OPM Federal Employee Viewpoint Survey
│   ├── brown_costsofwar/            # Brown University Costs of War Project
│   ├── csis/                        # CSIS Missile Defense Project data
│   ├── iiss/                        # IISS Military Balance extracts
│   ├── world_bank/                  # World Bank trade and GDP data
│   ├── sia/                         # Semiconductor Industry Association
│   ├── un_panels/                   # UN Panel of Experts reports
│   ├── academic_datasets/           # Jordan, Price decapitation datasets
│   └── congressional_testimony/     # Hearing transcripts
│
├── processed/                       # Cleaned, structured data ready for analysis
│   ├── weapon_system_costs.csv      # Standardized unit/lifecycle costs
│   ├── interceptor_costs.csv        # Missile defense system costs
│   ├── drone_costs.csv              # OWA and UAS cost estimates
│   ├── production_rates.csv         # Industrial production capacity
│   ├── engagement_log.csv           # Red Sea / Epic Fury engagement data
│   ├── economic_cascade.csv         # GDP impact estimates by scenario
│   ├── reconstruction_costs.csv     # Post-conflict cost accounting
│   ├── dew_costs.csv                # Directed energy cost-per-shot data
│   ├── legacy_vs_modern.csv         # Operating cost comparisons
│   ├── ic_workforce.csv             # IC demographic/attrition data
│   ├── acquisition_workforce.csv    # DoD acquisition workforce metrics
│   ├── decapitation_effects.csv     # Leadership targeting outcomes
│   └── succession_gaps.csv          # Key-person risk assessments
│
├── provenance/                      # Download logs and access records
│   ├── download_log.csv             # Date, URL, filename, SHA-256 hash
│   └── access_notes.md             # Paywalled sources, FOIA requests, etc.
│
├── scripts/                         # Data processing scripts
│   ├── extract_sar_costs.py         # Parse SAR PDFs to CSV
│   ├── extract_jbook_lines.py       # Parse J-Book procurement tables
│   ├── build_engagement_log.py      # Compile CENTCOM engagement data
│   ├── build_workforce_panel.py     # Process ODNI annual reports
│   └── validate_all.py              # Data integrity checks
│
└── codebook/                        # Variable definitions
    ├── weapon_systems_codebook.md
    ├── workforce_codebook.md
    └── engagement_codebook.md
```

---

## PART 1: PAPER 6 — COST ASYMMETRY DATA SOURCES

---

### Source 1: DoD Selected Acquisition Reports (SARs)

**What it contains:** Program-of-record unit costs, lifecycle costs, quantity procurement, schedule, and cost growth for every Major Defense Acquisition Program (MDAP). This is the single most authoritative source for U.S. weapon system costs.

**Where to access:**
- URL: https://www.esd.wis.mil/FOIA/Reading-Room/Reading-Room-List/
- Alternative: Search "Selected Acquisition Reports" at comptroller.defense.gov
- Alternative: OUSD(A&S) Acquisition Visibility portal
- CRS maintains digested versions — search CRS.gov for "Selected Acquisition Reports"

**Specific SARs to collect:**

| Program | SAR ID | Key Data Points |
|---------|--------|----------------|
| F-35 Joint Strike Fighter | F-35 SAR (latest: Dec 2024) | Unit recurring flyaway cost, program acquisition unit cost, total lifecycle, annual production rate |
| Columbia-class SSBN | Columbia SAR | Unit cost, construction timeline, industrial base constraints |
| Ford-class CVN | CVN-78 SAR | Unit cost, construction duration (7+ years), systems integration costs |
| Virginia-class SSN | Virginia SAR | Unit cost, Block V changes, production rate (2/year) |
| B-21 Raider | B-21 SAR | Unit cost (if declassified), production rate target |
| CH-53K King Stallion | CH-53K SAR | Unit cost, cost growth history |
| DDG-51 Flight III | DDG-51 SAR | Unit cost, production rate |

**Collection protocol:**
1. Download most recent SAR for each program (typically December edition, submitted to Congress in spring)
2. Save PDF to raw/dod_budget/sars/
3. Extract the following fields to weapon_system_costs.csv: program_name, sar_date, unit_cost_base_year, unit_cost_then_year, total_program_cost, total_quantity, production_rate_per_year, first_delivery_date
4. Record download date, URL, and SHA-256 hash in provenance/download_log.csv
5. Note: SARs use Base Year dollars and Then Year dollars — record BOTH and note the base year

**Pitfalls to avoid:**
- SARs report multiple cost metrics (PAUC, APUC, URF) — use Unit Recurring Flyaway (URF) for the CAR calculation as it most closely reflects marginal production cost
- Cost growth between SAR editions is significant — always use the most recent SAR and note any prior-year comparisons
- Some programs (B-21) have classified cost data — note in provenance/access_notes.md which figures are estimated vs. official

---

### Source 2: DoD Comptroller Budget Justification Documents (J-Books)

**What it contains:** Line-item procurement quantities and unit costs for every weapon system, ammunition type, and equipment purchase in the defense budget. More granular than SARs — includes individual missile variants, ammunition types, and modification programs.

**Where to access:**
- URL: https://comptroller.defense.gov/Budget-Materials/
- Navigate to the relevant fiscal year, then "Budget Justification Books"
- Each service publishes separate J-Books for Procurement, RDT&E, O&M, and Military Personnel

**Specific J-Books to collect:**

| J-Book | Service | Key Line Items |
|--------|---------|---------------|
| Missile Procurement, Army (MPA) | Army | Patriot PAC-3 MSE, THAAD interceptors, Stinger |
| Weapons Procurement, Navy (WPN) | Navy | SM-2 Block IIIC, SM-6 Block I/IA, Tomahawk, ESSM |
| Missile Procurement, Air Force | Air Force | AIM-120 AMRAAM, AIM-9X, JASSM-ER |
| Aircraft Procurement, Air Force | Air Force | F-35A unit cost, A-10 sustainment, MQ-9 Reaper |
| Shipbuilding and Conversion, Navy (SCN) | Navy | CVN-81, SSN-810+, DDG-51 Flight III |
| Procurement, Defense-Wide | OSD | Replicator program line items, counter-UAS systems |
| RDT&E, Defense-Wide | OSD | Directed energy programs, autonomous systems R&D |
| Operation and Maintenance | All | Flying hour costs by airframe (A-10 vs F-35 O&M comparison) |

**Collection protocol:**
1. Download the relevant J-Book PDFs for the most recent two fiscal years (FY2025 and FY2026 requests)
2. Save to raw/dod_budget/jbooks/
3. For interceptor costs: extract from WPN J-Book the line items for SM-2, SM-6, SM-3, ESSM — recording quantity, unit cost, total procurement
4. For drone costs: extract Replicator Initiative line items from Procurement, Defense-Wide
5. For operating cost comparison: extract from O&M J-Books the cost-per-flying-hour for A-10C and F-35A
6. Populate interceptor_costs.csv, drone_costs.csv, and legacy_vs_modern.csv

**Pitfalls to avoid:**
- J-Books report costs in Then Year dollars — convert to constant-year dollars for comparison using the OSD deflator tables (published in the National Defense Budget Estimates, "Green Book")
- Quantity and unit cost may reflect advance procurement in one year and full funding in another — read the narrative sections to understand the phasing
- The O&M J-Books report "cost per flying hour" but the definition varies by service — ensure you're comparing equivalent metrics

---

### Source 3: Congressional Research Service (CRS) Reports

**What it contains:** Independent, non-partisan analysis of defense programs, costs, and policy issues. CRS reports synthesize SAR data, J-Book data, and classified briefings into accessible summaries. Often the best single source for a non-specialist to understand a program's cost profile.

**Where to access:**
- URL: https://crsreports.congress.gov (free public access since 2018)
- Alternative: EveryCRSReport.com (searchable archive)

**Specific CRS reports to collect:**

| Report Number | Title / Topic | Author | Key Data |
|--------------|---------------|--------|----------|
| RL33745 | Navy Aegis BMD Program | Ronald O'Rourke | SM-6, SM-3 costs and inventories |
| R44463 | Navy Lasers, Railgun, and Gun-Launched Guided Projectile | Ronald O'Rourke | DEW cost-per-shot estimates |
| R44463 (updated) | Navy Laser Weapons | Ronald O'Rourke | HELIOS program status |
| R46925 | U.S. Military Operations in the Red Sea | Various | Epic Fury engagement counts, interceptor expenditure |
| R47201 | F-35 Joint Strike Fighter Program | Jeremiah Gertler | Unit cost history, sustainment costs |
| IF11235 | Precision-Guided Munitions: Background and Issues | Various | Munition costs and inventory levels |
| R46081 | Department of Defense Counter-UAS | Various | Counter-drone system costs |
| R44039 | A-10 Thunderbolt II | Jeremiah Gertler | Operating costs, retirement debate |
| R44968 | Columbia-Class Submarine Program | Ronald O'Rourke | Construction costs, schedule |
| R44972 | Ford-Class Aircraft Carrier | Ronald O'Rourke | CVN-78 cost, construction duration |
| (search) | Replicator Initiative / Autonomous Systems | Various | OWA drone procurement costs |

**Collection protocol:**
1. Search crsreports.congress.gov for each report number
2. Download PDF and save to raw/crs_reports/
3. CRS reports are excellent secondary sources that cite primary data (SARs, J-Books, classified briefings) — use them to locate primary sources and to cross-validate your SAR/J-Book extractions
4. Note: CRS reports are updated regularly — always check for the most recent version

---

### Source 4: CENTCOM Press Releases and Briefings — Operation Epic Fury

**What it contains:** Official engagement counts for Red Sea operations — how many drones, missiles, and boats were intercepted on specific dates. This is the raw data for calculating the defender's expenditure rate.

**Where to access:**
- URL: https://www.centcom.mil/MEDIA/PRESS-RELEASES/
- Filter by date range (November 2023 – present)
- Also: DoD Press Briefing transcripts at defense.gov/News/Transcripts/

**Collection protocol:**
1. Download every CENTCOM press release mentioning Houthi intercepts, Red Sea, or Operation Prosperity Guardian / Epic Fury
2. Save to raw/centcom/
3. Build engagement_log.csv with fields: date, target_type (drone/ASCM/ballistic_missile/USV), quantity_engaged, engagement_system (SM-2/SM-6/ESSM/CIWS/aircraft), location, source_url
4. For each engagement, compute estimated cost: quantity × interceptor_unit_cost
5. For the attacker side, estimate cost using CSIS/IISS data on Houthi system costs

**Pitfalls to avoid:**
- CENTCOM press releases sometimes report "destroyed" without specifying the interceptor used — note these as "system unspecified" and assign a range based on probable interceptor
- Engagement counts in press releases are sometimes cumulative over a period rather than per-day — read carefully to distinguish
- Some engagements involve aircraft (F/A-18, F-15E) rather than ship-based interceptors — the cost per engagement differs substantially

---

### Source 5: CSIS Missile Defense Project / Missile Threat Database

**What it contains:** Technical specifications and estimated costs for adversary missile and drone systems. The best open-source aggregation of Houthi/Iranian weapons data.

**Where to access:**
- URL: https://missilethreat.csis.org/
- Interactive database with system profiles
- Also: CSIS reports on Red Sea operations

**Collection protocol:**
1. Pull system profiles for: Shahed-136, Samad-series drones, Quds-series cruise missiles, Burkan/Toufan ballistic missiles
2. Record: system_name, type (OWA/cruise/ballistic), estimated_unit_cost_usd, range_km, warhead_kg, source_of_estimate
3. Save to drone_costs.csv (for OWA systems) and supplement interceptor_costs.csv (for what they were intercepted by)

---

### Source 6: GAO Reports — Industrial Base and Munitions

**What it contains:** Independent assessments of defense industrial base capacity, munitions production shortfalls, and supply chain vulnerabilities. Directly relevant to the "industrial tempo mismatch" domain.

**Where to access:**
- URL: https://www.gao.gov
- Search by topic: "defense industrial base," "munitions," "acquisition workforce"

**Specific GAO reports to collect:**

| Report Number | Title / Topic | Key Data |
|--------------|---------------|----------|
| GAO-23-106047 | Defense Industrial Base: DOD Should Take Actions | Production capacity, surge limitations |
| GAO-24-106164 | F-35 Sustainment: DoD Needs to Cut Costs | Cost-per-flying-hour, sustainment costs |
| GAO-23-105192 | Weapon System Sustainment | Operating costs across platforms |
| GAO-22-105075 | Defense Acquisitions Annual Assessment | Program cost growth, schedule delays |
| GAO-24-106337 | Foreign Investment: AFIDA (for MTS integration) | Already collected for Papers 1-4 |
| GAO-20-8 | Defense Acquisition Workforce | Workforce fragility, succession gaps (Paper 5) |
| GAO-22-104559 | DOD Acquisition Reform | Key-person risk in program management |
| GAO High-Risk List | Strategic Human Capital Management | Biennial workforce fragility assessment |

**Collection protocol:**
1. Download each report PDF
2. Save to raw/gao_reports/
3. Extract specific data tables and figures into processed CSVs
4. Cross-reference GAO findings with SAR/J-Book data for validation

---

### Source 7: Brown University Costs of War Project

**What it contains:** The most comprehensive accounting of post-9/11 war costs, including direct appropriations, future veteran care obligations, interest costs, and homeland security attributable spending. Essential for the "reconstruction burden" domain.

**Where to access:**
- URL: https://watson.brown.edu/costsofwar/
- Papers section contains detailed breakdowns
- Key researcher: Neta Crawford (now at Oxford)

**Collection protocol:**
1. Download the latest summary papers and data tables
2. Save to raw/brown_costsofwar/
3. Extract to reconstruction_costs.csv: category (direct_military, veteran_care, interest, homeland_security, other), amount_usd, time_period, conflict (Iraq/Afghanistan/Global), source_paper
4. The $8+ trillion total figure should be decomposable into subcategories for the paper

---

### Source 8: Economic Cascade / Trade Disruption Data

**What it contains:** GDP, trade volume, and supply chain dependency data for modeling economic cascade costs of conflict scenarios.

**Sources:**

| Source | URL | Data Type |
|--------|-----|-----------|
| World Bank Open Data | data.worldbank.org | GDP, trade volume, bilateral trade flows |
| IMF World Economic Outlook | imf.org/en/Publications/WEO | GDP forecasts, trade disruption scenarios |
| Semiconductor Industry Association | semiconductors.org | TSMC market share, wafer production concentration |
| IEA Critical Minerals Data Explorer | iea.org | Already used in Paper 4 — mineral trade flows |
| UN COMTRADE | comtrade.un.org | Bilateral trade data by commodity |
| Federal Reserve FRED | fred.stlouisfed.org | U.S. economic indicators, historical GDP |

**Collection protocol:**
1. For Taiwan scenario: pull TSMC's share of advanced semiconductor production (<7nm) from SIA reports
2. For Hormuz scenario: pull oil transit volume data from EIA (eia.gov) and fertilizer trade data from ITC Trade Map
3. For GDP impact: pull baseline GDP for U.S. and China from World Bank, then apply disruption multipliers from CBO/RAND scenario analyses
4. Save to economic_cascade.csv: scenario, sector_affected, baseline_value_usd, disruption_percentage, cascade_multiplier, total_impact, source

---

### Source 9: Directed Energy Weapons Data

**What it contains:** Cost-per-shot estimates, power requirements, and operational status of DEW programs.

**Sources:**

| Program | Source | Key Data |
|---------|--------|----------|
| Navy HELIOS (60kW+ laser) | CRS R44463, Navy PB exhibits | Cost per engagement, installation cost |
| Army DE M-SHORAD | Army budget justification, PEO MS briefings | Unit cost, cost-per-shot estimate |
| Air Force SHIELD (Self-Protect High Energy Laser Demonstrator) | Air Force RDT&E J-Book | Development cost, target TRL |
| DARPA LANCE (Laser Advancements for Next-generation Compact Environments) | DARPA budget justification | Research cost, target specifications |

**Collection protocol:**
1. The cost-per-shot for DEWs is estimated at $1-$10 per engagement (electricity cost) vs $1M-$4M for kinetic interceptors — source this from CRS reports and DoD testimony
2. Extract to dew_costs.csv: system_name, type (SSL/fiber/chemical), power_kw, cost_per_engagement_usd, platform_acquisition_cost, source
3. Note: DEW cost-per-shot estimates vary widely depending on assumptions about power generation costs — document the assumptions

---

### Source 10: Legacy Platform Cost Comparison

**What it contains:** Operating cost per flying hour, sortie rate, and mission effectiveness data for A-10 vs F-35 and other legacy-vs-modern comparisons.

**Sources:**
- Air Force O&M J-Book: cost-per-flying-hour by airframe (Table O-1)
- GAO-24-106164 (F-35 sustainment costs)
- CRS R44039 (A-10 program)
- Air Force Magazine / Air & Space Forces Magazine reporting on per-hour costs

**Collection protocol:**
1. Extract cost-per-flying-hour for: A-10C, F-35A, F-16C, F-15E, MQ-9
2. Record: airframe, cost_per_flying_hour_usd, fiscal_year, source
3. For sortie comparison: record sortie rate (sorties per day per aircraft), loiter time, weapons load, and weapons delivery cost
4. Save to legacy_vs_modern.csv

---

## PART 2: PAPER 5 — HUMAN CAPITAL DATA SOURCES

---

### Source 11: ODNI Annual Demographic Report

**What it contains:** Aggregate IC workforce statistics — total headcount across 18 IC elements, demographic breakdown, hiring rates, attrition rates, and workforce composition.

**Where to access:**
- URL: https://www.dni.gov/index.php/who-we-are/organizations/ic-equal-employment-opportunity-and-diversity/ic-workforce-demographics
- Published annually (typically June-August for prior fiscal year data)

**Collection protocol:**
1. Download reports for the most recent 5 years (FY2020-FY2024)
2. Save to raw/odni/
3. Extract to ic_workforce.csv: fiscal_year, total_headcount, hiring_rate, attrition_rate, avg_age, avg_tenure_years, retirement_eligible_pct, demographic breakdowns
4. Track year-over-year attrition trends — this is the "below-threshold erosion" that HCTS predicts is the primary threat

**Pitfalls to avoid:**
- ODNI reports aggregate across all 18 IC elements — agency-level breakdowns are limited
- Some workforce categories are classified — note which figures are available vs. estimated
- Attrition rates may not distinguish between retirement, resignation, and involuntary separation — note the definitions used

---

### Source 12: OPM Federal Employee Viewpoint Survey (FEVS)

**What it contains:** Survey data on federal employee satisfaction, retirement intentions, knowledge transfer effectiveness, and supervisory quality — across all federal agencies including IC elements that participate.

**Where to access:**
- URL: https://www.opm.gov/fevs/
- Governmentwide and agency-level results available
- Raw data files available for download (requires registration)

**Collection protocol:**
1. Download agency-level results for DoD, DHS, DOE (national labs), and any IC agencies that participate
2. Key variables: Q1 (retirement intention within 1 year), Q2 (retirement intention within 5 years), satisfaction with knowledge transfer, perception of succession readiness
3. Save to raw/opm/ and extract relevant variables to processed CSVs
4. The retirement intention data is a direct proxy for the "retirement horizon" variable in the HCTS simulator

---

### Source 13: GAO Strategic Human Capital Management (High-Risk)

**What it contains:** Biennial assessment of workforce fragility across the federal government, including specific findings on mission-critical skills gaps, succession planning failures, and key-person risk.

**Where to access:**
- URL: https://www.gao.gov/high-risk-list
- Strategic Human Capital Management has been on the High-Risk List since 2001
- Search GAO.gov for "strategic human capital" for individual reports

**Specific reports:**

| Report | Key Data |
|--------|----------|
| GAO-23-106203 | High-Risk Series: Efforts to Address Government-wide Personnel Practices |
| GAO-21-119SP | High-Risk Series: Dedicated Leadership Needed to Address Limited Progress |
| GAO-19-157SP | High-Risk Series: Substantial Efforts Needed to Achieve Greater Progress |

**Collection protocol:**
1. Download each biennial update
2. Extract specific findings on: mission-critical skills gaps, succession planning metrics, retirement wave projections, knowledge transfer program effectiveness
3. Record in succession_gaps.csv: agency, function, gap_type, severity, year_reported, mitigation_status

---

### Source 14: DoD Acquisition Workforce Reports

**What it contains:** Size, composition, certification levels, experience distribution, and succession planning metrics for the defense acquisition workforce — the Tier 2 (authority holder) population in HCTS terms.

**Where to access:**
- URL: https://www.hci.mil/ (Human Capital Initiatives, OUSD(A&S))
- DoD Acquisition Workforce Strategic Plan
- Annual Report to Congress on Acquisition Workforce

**Collection protocol:**
1. Download the most recent Acquisition Workforce Strategic Plan and Annual Report
2. Save to raw/dod_budget/acquisition_workforce/
3. Extract to acquisition_workforce.csv: fiscal_year, total_workforce_size, avg_years_experience, certification_levels (1/2/3), retirement_eligible_pct, avg_time_in_current_position, key_leadership_positions_vacant
4. Cross-reference with GAO reports on specific program manager succession gaps

---

### Source 15: Leadership Decapitation Datasets

**What it contains:** Systematic data on the effects of targeted killing / leadership removal on organizational capacity. Essential for the deterrence argument in HCTS.

**Sources:**

| Dataset | Author | Published | Coverage |
|---------|--------|-----------|----------|
| Leadership Decapitation Database | Jenna Jordan | Security Studies, 2009 (updated) | 298 incidents, 1945-2004 |
| Decapitation and Organizational Resilience | Bryan Price | Journal of Conflict Resolution, 2012 | Leadership targeting, organizational mortality |
| Global Terrorism Database | START, University of Maryland | Continuously updated | Cross-reference for org capacity pre/post |

**Where to access:**
- Jordan dataset: contact author or check journal supplementary materials at tandfonline.com
- Price dataset: check journal supplementary materials at SAGE Journals
- GTD: https://www.start.umd.edu/gtd/

**Collection protocol:**
1. Obtain Jordan and Price datasets (may require author contact or institutional access)
2. Save to raw/academic_datasets/
3. Code relevant cases into decapitation_effects.csv: organization, leader_removed, date, method (killed/captured/defected), organizational_outcome (degraded/survived/collapsed), time_to_outcome_months, successor_available (Y/N)
4. The Jordan finding (decapitation rarely achieves intended effect) and the Johnston qualification (it works when non-transferable capabilities are targeted) are central to the HCTS deterrence argument

---

### Source 16: CIA Center for the Study of Intelligence — Studies in Intelligence

**What it contains:** Retrospective analyses of intelligence workforce transitions, analytical methodology, and institutional learning. The unclassified edition contains valuable historical case study material.

**Where to access:**
- URL: https://www.cia.gov/resources/csi/studies-in-intelligence/
- Unclassified articles available for download
- Back issues searchable by topic

**Collection protocol:**
1. Search for articles on: workforce transition, Cold War drawdown, analytical tradecraft, knowledge management, mentoring, succession
2. Download relevant articles to raw/congressional_testimony/ (or create raw/cia_csi/)
3. These are qualitative sources for the historical case studies — extract specific data points (dates, headcounts, capability assessments) to support the CIA post-Cold War generation gap narrative
4. Also search for articles on the post-9/11 hiring surge — the rapid expansion created different workforce fragility than the drawdown

---

### Source 17: Congressional Commission Reports

**What it contains:** Major commission reports on intelligence community failures that document specific workforce capability gaps.

| Report | Key Data for HCTS |
|--------|-------------------|
| 9/11 Commission Report (2004) | Pre-9/11 analytical gaps, HUMINT workforce shortfalls, language capability gaps |
| WMD Commission (Silberman-Robb, 2005) | Iraq WMD analytical failures, workforce quality assessment |
| Cybersecurity Commission (various) | Cyber workforce shortage quantification |
| National Defense Strategy Commission (2018) | Workforce readiness assessment |
| National Security Commission on AI (2021) | AI/technical workforce gaps in national security |

**Where to access:**
- Most available at govinfo.gov or commission-specific websites
- 9/11 Report: https://govinfo.gov/content/pkg/GPO-911REPORT/pdf/GPO-911REPORT.pdf

**Collection protocol:**
1. Download each report
2. Extract specific workforce findings: headcount gaps, skill shortages, succession failures, recommendations
3. These provide the historical evidence for Tier 1 (knowledge holder) and Tier 2 (authority holder) fragility

---

### Source 18: NNSA/DOE Nuclear Weapons Workforce Data

**What it contains:** Workforce demographics, skills assessments, and succession planning for the nuclear weapons complex — the most extreme example of Tier 1 key-person dependency.

**Where to access:**
- NNSA Stockpile Stewardship and Management Plan (published to Congress annually)
- URL: https://www.energy.gov/nnsa
- Also: National Academies reports on nuclear weapons workforce (search nap.edu)

**Collection protocol:**
1. Download the latest Stockpile Stewardship and Management Plan
2. Extract workforce metrics: total weapons workforce, average age, retirement eligible percentage, critical skills gaps
3. The NNSA workforce illustrates the most extreme HCTS case: weapons designers whose knowledge of specific warhead physics is non-transferable and whose retirement creates irreplaceable capability loss
4. National Academies reports provide independent assessments of workforce sustainability

---

## PART 3: SHARED / INTEGRATION DATA

---

### Source 19: DoD OSD Deflator Tables (Green Book)

**What it contains:** Deflator indices for converting between Then Year and constant-year dollars. Essential for making cost comparisons across fiscal years.

**Where to access:**
- URL: https://comptroller.defense.gov/Budget-Materials/
- Published as "National Defense Budget Estimates" (informally "Green Book")
- Table 5-6: Deflators

**Collection protocol:**
1. Download the most recent Green Book
2. Extract the DoD deflator table
3. Apply deflators to all cost data to produce constant FY2024 dollar figures
4. All cost comparisons in the papers must use constant-year dollars

---

### Source 20: Existing MTS Data (Papers 1-4)

**What it contains:** The 1,637-dependency supply chain ledger, AFIDA holdings data, CFIUS Appendix A installation database, and SECMap ownership chain results from the existing research programme.

**Where to access:**
- github.com/rjgreenresearch/mts-doctrine-simulator
- github.com/rjgreenresearch/secmap
- github.com/rjgreenresearch/cfius-jurisdiction-analysis

**Integration notes:**
- The supply chain dependency ledger (CSV) from mts-doctrine-simulator provides the Material MTS pillar input
- The AFIDA-CFIUS intersection provides the compound detection probability (3.6%) that links the empirical papers to the theoretical framework
- The Strait of Hormuz cascade scenario from the MTS simulator provides real-time validation data for the economic cascade domain in Paper 6

---

## PART 4: COLLECTION PROTOCOLS

---

### Protocol 1: Download Logging

Every file downloaded must be logged in provenance/download_log.csv:

```
date,source_name,url,filename,sha256_hash,notes
2026-04-18,DoD Comptroller,https://comptroller.defense.gov/...,FY2026_PB_WPN.pdf,abc123...,Navy WPN J-Book FY2026
```

Run `sha256sum` on every downloaded file immediately and record the hash. This ensures data integrity and enables verification that the raw files have not been modified.

### Protocol 2: PDF Data Extraction

Most federal sources are PDF. Extraction protocol:
1. First attempt: use tabula-py or camelot for table extraction
2. If tables don't parse cleanly: manual extraction with double-entry verification (enter data twice independently, compare for discrepancies)
3. Record the page number and table number from the source PDF in every processed CSV row
4. For narrative data (qualitative findings from GAO/CRS): extract relevant paragraphs with page citations

### Protocol 3: Constant-Dollar Conversion

All cost figures must be converted to constant FY2024 dollars using DoD deflators:
1. Identify the dollar-year of each source figure (Then Year, Base Year, or specific FY)
2. Apply the appropriate deflator from the Green Book
3. Record both the original figure and the deflated figure in the processed CSV
4. Fields: original_value, original_dollar_year, deflated_value_fy2024

### Protocol 4: Source Triangulation

For every key data point used in the papers, attempt to verify from at least two independent sources:
- Primary: SAR or J-Book (official DoD data)
- Secondary: CRS report (independent analysis)
- Tertiary: GAO report (independent audit)

Record the triangulation in the processed CSV: primary_source, secondary_source, values_consistent (Y/N), discrepancy_notes

### Protocol 5: Classified Data Boundaries

Some data points are classified or restricted. Protocol:
1. Never attempt to access classified information
2. If a figure is estimated rather than official, mark it clearly: source_type = "estimate" vs "official"
3. If a CRS or GAO report references classified briefings, note this as: source_type = "CRS_citing_classified"
4. Document in provenance/access_notes.md any data that could not be obtained and the reason

---

## PART 5: CHECKLISTS

---

### Paper 6 Data Completeness Checklist

- [ ] SAR data extracted for at least 5 major platforms (F-35, Columbia, CVN-78, Virginia, DDG-51)
- [ ] Interceptor unit costs sourced from J-Books (SM-2, SM-6, SM-3, ESSM, PAC-3 MSE)
- [ ] OWA drone costs estimated from CSIS/IISS (at least 3 system types)
- [ ] Replicator Initiative procurement data from Defense-Wide J-Book
- [ ] Epic Fury engagement log compiled from CENTCOM releases (at least 20 dated entries)
- [ ] Cost-per-flying-hour data for A-10C and F-35A from O&M J-Books
- [ ] DEW cost-per-shot estimates from CRS and DoD testimony
- [ ] Industrial production rate data from at least 2 GAO industrial base reports
- [ ] Brown University Costs of War total and subcategory breakdown
- [ ] GDP and trade data for Taiwan and Hormuz scenarios from World Bank/IMF
- [ ] TSMC advanced semiconductor market share from SIA
- [ ] All costs converted to constant FY2024 dollars using Green Book deflators
- [ ] CAR calculated for at least 4 offense-defense system pairs
- [ ] provenance/download_log.csv complete with SHA-256 hashes for all files

### Paper 5 Data Completeness Checklist

- [ ] ODNI Annual Demographic Reports downloaded for FY2020-FY2024
- [ ] IC workforce attrition rates extracted year-over-year
- [ ] OPM FEVS retirement intention data for DoD/DHS/DOE
- [ ] GAO High-Risk List Strategic Human Capital updates (at least 2 most recent)
- [ ] DoD Acquisition Workforce Strategic Plan and Annual Report
- [ ] Jordan leadership decapitation dataset obtained or documented
- [ ] Price decapitation dataset obtained or documented
- [ ] Studies in Intelligence articles on workforce transitions downloaded
- [ ] 9/11 Commission and WMD Commission workforce findings extracted
- [ ] NNSA Stockpile Stewardship workforce data extracted
- [ ] succession_gaps.csv populated with at least 10 documented gaps
- [ ] ic_workforce.csv populated with 5-year panel data

### Integration Checklist

- [ ] mts-doctrine-simulator dependency ledger (1,637 entries) accessible
- [ ] Supply chain cascade scenario data (Hormuz) loadable by cost-asymmetry-simulator
- [ ] HCDI computation validated against at least 3 test cases
- [ ] CAR computation validated against Epic Fury primary data
- [ ] Three-pillar compound deterrence assessment produces consistent results across all three tools
- [ ] All processed CSVs have codebook entries in codebook/ directory
- [ ] README.md documents data provenance, licensing, and citation requirements

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-04-18 | 1.0 | Initial catalog covering Papers 5 and 6 |
