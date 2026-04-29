"""
cas/utils.py
Utility functions: run ID generation, output directory management,
file I/O helpers, and formatted console tables.
"""

import os
import json
import csv
from datetime import datetime
from typing import Any


# ── Run ID / output directory ─────────────────────────────────────────────────

def make_run_id(prefix: str = "run") -> str:
    """
    Generate a sortable run identifier: run_YYYYMMDD_HHMMSS
    e.g.  run_20260428_143022
    """
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def make_run_dir(base_output: str, run_id: str) -> str:
    """
    Create and return the run-specific output directory.
    Path: <base_output>/<run_id>/
    """
    run_dir = os.path.join(base_output, run_id)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def stamped_filename(run_dir: str, stem: str, ext: str) -> str:
    """
    Return a full path for an output file inside run_dir.
    e.g.  stamped_filename('output/run_20260428_143022', 'report', 'html')
          → 'output/run_20260428_143022/report.html'
    """
    return os.path.join(run_dir, f"{stem}.{ext}")


# ── JSON helpers ──────────────────────────────────────────────────────────────

def write_json(data: Any, path: str, indent: int = 2) -> None:
    """Write data to a JSON file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, default=str)


def read_json(path: str) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ── CSV helpers ───────────────────────────────────────────────────────────────

def write_csv(rows: list[dict], path: str) -> None:
    """Write a list of dicts to CSV."""
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# ── Console table formatter ───────────────────────────────────────────────────

def print_table(rows: list[dict], title: str = "", col_widths: dict | None = None) -> None:
    """
    Print a list-of-dicts as a plain-text table to stdout.
    col_widths: optional dict mapping key → column width.
    """
    if not rows:
        return
    keys = list(rows[0].keys())
    widths = col_widths or {k: max(len(str(k)),
                                   max(len(str(r.get(k, ""))) for r in rows))
                             for k in keys}
    sep = "  ".join("-" * widths[k] for k in keys)
    hdr = "  ".join(str(k).ljust(widths[k]) for k in keys)

    if title:
        print(f"\n  {title}")
        print("  " + "─" * len(sep))
    print("  " + hdr)
    print("  " + sep)
    for row in rows:
        line = "  ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys)
        print("  " + line)


# ── Metadata manifest ─────────────────────────────────────────────────────────

def write_manifest(run_dir: str, meta: dict) -> str:
    """
    Write a run_manifest.json containing run metadata (id, timestamp,
    config paths, n_sims, etc.) to the run directory.
    Returns the manifest file path.
    """
    meta["generated_at"] = datetime.now().isoformat()
    path = os.path.join(run_dir, "run_manifest.json")
    write_json(meta, path)
    return path
