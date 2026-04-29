"""
cas/cli.py
Command-line interface for the Cost-Asymmetry Simulator (CAS).

Usage examples
--------------
  python -m cas                          # run with all defaults
  python -m cas --n-sims 5000 --horizon 60
  python -m cas --budget 2.0 --report html,pdf
  python -m cas --weapon-config my_weapons.yaml --scenario two_war_surge
  python -m cas --list-systems
  python -m cas --help
"""

import argparse
import sys
import os
import logging

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m cas",
        description=(
            "Cost-Asymmetry Simulator (CAS) v%(ver)s\n"
            "MTS Pillar 3 — Paper 6: The Cost Curve as Deterrent\n\n"
            "Models Cost Asymmetry Ratios, two-war inventory depletion, "
            "and Monte Carlo portfolio optimisation for US military munitions.\n"
            "All data is sourced from publicly available US government "
            "documents (CRS, CSIS, SAR, CENTCOM, DoD budget docs)."
        ) % {"ver": __version__},
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Output files are written to output/<run_id>/ and stamped with\n"
            "the run timestamp (e.g. run_20260428_143022).\n\n"
            "Configuration files are in config/ and are plain YAML — edit\n"
            "weapon_systems.yaml to add new systems or update cost data.\n\n"
            "Paper 6 SSRN: to be posted | github.com/rjgreenresearch"
        ),
    )

    # ── Simulation parameters ─────────────────────────────────────────────────
    sim = p.add_argument_group("Simulation parameters")
    sim.add_argument(
        "--n-sims", type=int, default=None,
        metavar="N",
        help="Number of Monte Carlo simulations per system (default: from simulation.yaml).",
    )
    sim.add_argument(
        "--horizon", type=int, default=None,
        metavar="DAYS",
        help="Simulation horizon in days (default: 90; two-war standard).",
    )
    sim.add_argument(
        "--budget", type=float, default=1.0,
        metavar="BILLION_USD",
        help="Budget for portfolio optimisation in $B (default: 1.0).",
    )
    sim.add_argument(
        "--scenario", type=str, default=None,
        metavar="NAME",
        help=(
            "Named scenario from simulation.yaml "
            "(two_war_baseline | two_war_surge | single_war_extended | deterrence_optimal). "
            "Overrides --horizon and production surge settings."
        ),
    )
    sim.add_argument(
        "--surge", type=float, default=0.0,
        metavar="FRACTION",
        help="Production surge fraction for readiness runs (e.g. 0.5 = +50%%; default: 0.0).",
    )
    sim.add_argument(
        "--cap-tier", type=str, default=None,
        metavar="TIER:FRACTION",
        help=(
            "Override allocation cap for one tier (e.g. INFANTRY_CUAS:0.05). "
            "Can be specified multiple times. "
            "Fractions are 0.0–1.0; use 1.0 to disable a cap. "
            "Example: --cap-tier STRATEGIC:0.60 --cap-tier INFANTRY_CUAS:0.05"
        ),
        action="append",
        dest="cap_tiers",
    )
    sim.add_argument(
        "--cap-system", type=float, default=None,
        metavar="FRACTION",
        help=(
            "Override the per-system allocation cap (default: from simulation.yaml). "
            "No single system will receive more than this fraction of total budget. "
            "Example: --cap-system 0.20"
        ),
    )

    # ── Configuration overrides ───────────────────────────────────────────────
    cfg = p.add_argument_group("Configuration overrides")
    cfg.add_argument(
        "--weapon-config", type=str, default=None,
        metavar="PATH",
        help="Path to custom weapon_systems.yaml (default: config/weapon_systems.yaml).",
    )
    cfg.add_argument(
        "--threat-config", type=str, default=None,
        metavar="PATH",
        help="Path to custom threat_systems.yaml (default: config/threat_systems.yaml).",
    )
    cfg.add_argument(
        "--sim-config", type=str, default=None,
        metavar="PATH",
        help="Path to custom simulation.yaml (default: config/simulation.yaml).",
    )

    # ── Output options ────────────────────────────────────────────────────────
    out = p.add_argument_group("Output options")
    out.add_argument(
        "--output-dir", type=str, default="output",
        metavar="DIR",
        help="Base output directory (default: output/). Run files go in <DIR>/<run_id>/.",
    )
    out.add_argument(
        "--report", type=str, default="html",
        metavar="FORMATS",
        help=(
            "Comma-separated report formats: html,pdf,json,csv or 'none' "
            "(default: html). Example: --report html,pdf"
        ),
    )
    out.add_argument(
        "--run-id", type=str, default=None,
        metavar="ID",
        help="Override the auto-generated run ID (default: run_YYYYMMDD_HHMMSS).",
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    log_grp = p.add_argument_group("Logging")
    log_grp.add_argument(
        "--log-level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console log level (default: INFO).",
    )

    # ── Informational commands ────────────────────────────────────────────────
    info = p.add_argument_group("Informational")
    info.add_argument(
        "--list-systems", action="store_true",
        help="Print all configured weapon and threat systems then exit.",
    )
    info.add_argument(
        "--version", action="version",
        version=f"CAS v{__version__}",
    )

    return p


def list_systems(cfg) -> None:
    """Print configured systems to stdout."""
    print(f"\nWeapon systems ({len(cfg.weapons)}):")
    print(f"  {'ID':<24} {'Tier':<22} {'Unit Cost':>12} {'Inventory':>10} {'Quality':>8}")
    print("  " + "-" * 82)
    for k, ws in sorted(cfg.weapons.items()):
        uc = ws.get("unit_cost_per_shot", ws.get("unit_cost", 0))
        print(f"  {k:<24} {ws.get('tier','—'):<22} ${uc:>11,} "
              f"{ws.get('inventory_est', 0):>10,} {ws.get('quality_tier','—'):>8}")

    print(f"\nThreat systems ({len(cfg.threats)}):")
    print(f"  {'ID':<36} {'Origin':<12} {'Unit Cost':>12} {'Dud%':>6}")
    print("  " + "-" * 72)
    for k, t in sorted(cfg.threats.items()):
        print(f"  {k:<36} {t.get('origin','—'):<12} "
              f"${t.get('unit_cost',0):>11,} "
              f"{t.get('dud_rate',0)*100:>5.0f}%")


def parse_args(argv=None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv=None) -> int:
    """
    CAS entry point. Returns exit code (0 = success).
    Called by python -m cas via __main__.py.
    """
    args = parse_args(argv)

    # ── Bootstrap logging early (before Config, which logs during init) ───────
    from .utils import make_run_id, make_run_dir, write_manifest
    from .logging_config import setup_logging

    run_id  = args.run_id or make_run_id()
    run_dir = make_run_dir(args.output_dir, run_id)
    log     = setup_logging(run_dir, console_level=args.log_level,
                            file_level="DEBUG")
    log.info("CAS v%s | run_id=%s", __version__, run_id)

    # ── Load configuration ────────────────────────────────────────────────────
    from .config import Config
    cfg = Config(
        weapon_systems_path=args.weapon_config,
        threat_systems_path=args.threat_config,
        simulation_path=args.sim_config,
    )
    log.info("Config loaded: %s", cfg.summary())

    # ── --list-systems shortcut ───────────────────────────────────────────────
    if args.list_systems:
        list_systems(cfg)
        return 0

    # ── Override config with CLI flags ────────────────────────────────────────
    if args.n_sims:
        cfg.n_sims = args.n_sims
        log.info("CLI override: n_sims=%d", cfg.n_sims)

    horizon = args.horizon or cfg.horizon("long")
    if args.scenario and args.scenario in cfg.scenarios:
        sc = cfg.scenarios[args.scenario]
        horizon = sc.get("horizon_days", horizon)
        args.surge = sc.get("production_surge_pct", args.surge)
        log.info("Scenario '%s': horizon=%d  surge=%.0f%%",
                 args.scenario, horizon, args.surge * 100)

    report_formats = [f.strip().lower()
                      for f in args.report.split(",")
                      if f.strip().lower() != "none"]

    # ── Run simulations ───────────────────────────────────────────────────────
    # ── Run simulations ───────────────────────────────────────────────────────
    from .simulator   import compute_car_matrix, two_war_depletion, marginal_value
    from .mc_simulator import run_full_mc, optimise_portfolio
    from .utils        import write_json, write_csv, stamped_filename

    try:
        log.info("Computing CAR matrix...")
        car_rows = compute_car_matrix(cfg)

        log.info("Computing two-war depletion (horizon=%d days)...", horizon)
        dep_rows = two_war_depletion(cfg, horizon)

        log.info("Computing marginal value...")
        marg_rows = marginal_value(cfg)
        for r in marg_rows:
            unit_cost = r["unit_cost"]
            ws = cfg.weapons.get(r["system"], {})
            cr = ws.get("consumption_rates", {})
            daily = (cr.get("theater_1", {}).get("mean", 0)
                   + cr.get("theater_2", {}).get("mean", 0))
            annual = ws.get("annual_production",
                     ws.get("annual_production_target", 0))
            net = max(0.0, daily - annual / 365.0)
            r["days_per_1000M"] = (
                round(1e9 / unit_cost / net, 1)
                if net > 0 and unit_cost > 0 else "inf"
            )

        log.info("Running Monte Carlo (n=%d, horizon=%d)...", cfg.n_sims, horizon)
        mc_results = run_full_mc(cfg, horizon)

        # Apply any CLI cap overrides into cfg.portfolio_caps
        if args.cap_tiers:
            for item in args.cap_tiers:
                try:
                    tier, frac_str = item.split(":", 1)
                    frac = float(frac_str)
                    if not 0.0 <= frac <= 1.0:
                        raise ValueError(f"Fraction must be 0.0–1.0, got {frac}")
                    cfg.portfolio_caps[tier.strip().upper()] = frac
                    log.info("CLI cap override: %s → %.0f%%",
                             tier.strip().upper(), frac * 100)
                except (ValueError, AttributeError) as exc:
                    log.warning("Invalid --cap-tier value '%s': %s", item, exc)

        if args.cap_system is not None:
            if 0.0 <= args.cap_system <= 1.0:
                cfg.portfolio_caps["_per_system"] = args.cap_system
                log.info("CLI per-system cap override: %.0f%%",
                         args.cap_system * 100)
            else:
                log.warning("--cap-system %.2f out of range [0,1]; ignored",
                            args.cap_system)

        log.info("Running portfolio optimisation (budget=$%.1fB)...", args.budget)
        portfolio = optimise_portfolio(cfg, args.budget, horizon)

    except KeyboardInterrupt:
        log.warning("Run interrupted by user (Ctrl+C)")
        print("\n  Run interrupted.")
        return 130

    except FileNotFoundError as exc:
        log.error("File not found: %s", exc)
        print(f"\n  ERROR: {exc}")
        return 1

    except (ValueError, KeyError) as exc:
        log.error("Configuration error: %s", exc)
        print(f"\n  CONFIG ERROR: {exc}")
        print("  Re-run with --log-level DEBUG for details.")
        return 2

    except MemoryError:
        log.error("Out of memory — reduce --n-sims")
        print("\n  ERROR: Out of memory. Try: python -m cas --n-sims 1000")
        return 3

    except Exception as exc:
        log.exception("Unexpected error: %s", exc)
        print(f"\n  ERROR: {exc}")
        print(f"  Full traceback -> {run_dir}/cas.log")
        return 99

    # ── Write outputs ─────────────────────────────────────────────────────────
    try:
        if "json" in report_formats or True:
            write_json({"car_matrix": car_rows,
                        "depletion":  dep_rows,
                        "mc":         mc_results,
                        "marginal":   marg_rows,
                        "portfolio":  portfolio},
                       stamped_filename(run_dir, "results", "json"))
            log.info("JSON results written")

        if "csv" in report_formats:
            write_csv(car_rows,  stamped_filename(run_dir, "car_matrix", "csv"))
            write_csv(dep_rows,  stamped_filename(run_dir, "depletion",  "csv"))
            write_csv(marg_rows, stamped_filename(run_dir, "marginal",   "csv"))
            log.info("CSV files written")

        if "html" in report_formats:
            from .reporter import generate_html
            generate_html(run_id, car_rows, dep_rows, mc_results,
                          marg_rows, portfolio,
                          stamped_filename(run_dir, "report", "html"),
                          horizon)

        if "pdf" in report_formats:
            from .reporter import generate_pdf
            generate_pdf(run_id, car_rows, dep_rows, mc_results,
                         marg_rows, portfolio,
                         stamped_filename(run_dir, "report", "pdf"),
                         horizon)

    except OSError as exc:
        log.error("Output write error: %s", exc)
        print(f"\n  OUTPUT ERROR: {exc}")
        print("  Simulation completed but output could not be written.")
        return 4

    except ImportError as exc:
        log.error("Missing dependency for report format: %s", exc)
        print(f"\n  DEPENDENCY ERROR: {exc}")
        print("  Install missing packages: pip install -r requirements.txt")
        return 5

    # Manifest (best-effort — don't fail run if manifest write fails)
    try:
        write_manifest(run_dir, {
            "run_id":       run_id,
            "version":      __version__,
            "n_sims":       cfg.n_sims,
            "horizon_days": horizon,
            "budget_B":     args.budget,
            "scenario":     args.scenario,
            "formats":      report_formats,
            "weapon_count": len(cfg.weapons),
            "threat_count": len(cfg.threats),
        })
    except Exception as exc:
        log.warning("Manifest write failed (non-fatal): %s", exc)

    log.info("Run complete -> %s", run_dir)
    print(f"\n  Output: {run_dir}/")
    return 0
