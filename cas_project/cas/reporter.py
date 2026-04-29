"""
cas/reporter.py
Generates HTML and PDF reports from simulation results.
Charts are produced with matplotlib and embedded as base64 PNG
so reports are fully self-contained single files.
"""

import base64
import io
import logging
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")           # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from jinja2 import Environment, FileSystemLoader, select_autoescape
from fpdf import FPDF

from . import __version__

log = logging.getLogger("cas.reporter")

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# ── Colour palette ────────────────────────────────────────────────────────────
TIER_COLOURS = {
    "STRATEGIC":         "#1a1a2e",
    "OPERATIONAL":       "#16213e",
    "PRECISION_STRIKE":  "#0f3460",
    "ATTRITION_OFFENSE": "#533483",
    "ATTRITION_DEFENSE": "#e94560",
    "STRUCTURAL_SOLUTION":"#00b4d8",
}
STATUS_COLOURS = {
    "ACUTE_CRISIS":   "#d62828",
    "CRITICAL":       "#f77f00",
    "HIGH_RISK":      "#fcbf49",
    "MEDIUM_RISK":    "#eae2b7",
    "LOW_RISK":       "#4caf50",
    "SELF_SUSTAINING":"#2e7d32",
}


# ─────────────────────────────────────────────────────────────────────────────
# Chart generators — each returns a base64 PNG string
# ─────────────────────────────────────────────────────────────────────────────

def _b64(fig) -> str:
    """Render a matplotlib figure to base64 PNG and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("ascii")
    plt.close(fig)
    return data


def chart_car_matrix(car_rows: list[dict]) -> str:
    """Horizontal bar chart of CAR values, colour-coded by advantage."""
    labels = [r["label"] for r in car_rows]
    values = [min(r["CAR_raw"], 500) for r in car_rows]   # cap for display
    colours = ["#d62828" if r["interpretation"] == "ADV_ADVANTAGE"
               else "#4caf50" if r["interpretation"] == "US_ADVANTAGE"
               else "#f77f00"
               for r in car_rows]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.45)))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    bars = ax.barh(labels, values, color=colours, edgecolor="#444", linewidth=0.4)
    ax.axvline(1.0, color="#ffffff", lw=1.0, ls="--", label="Parity (CAR=1)")

    for bar, r in zip(bars, car_rows):
        disp = f"{r['CAR_raw']:.0f}" if r["CAR_raw"] > 10 else f"{r['CAR_raw']:.3f}"
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                disp, va="center", fontsize=7, color="#cccccc")

    ax.set_xlabel("Cost Asymmetry Ratio (threat cost / defense cost)", color="#cccccc")
    ax.tick_params(colors="#cccccc", labelsize=8)
    ax.spines[:].set_color("#555")
    ax.invert_yaxis()

    legend_patches = [
        mpatches.Patch(color="#d62828", label="Adversary advantage (CAR<1)"),
        mpatches.Patch(color="#4caf50", label="US advantage (CAR>1)"),
        mpatches.Patch(color="#f77f00", label="Parity"),
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              facecolor="#2a2a3e", labelcolor="#cccccc", fontsize=7)
    ax.set_title("Figure 1 — Cost Asymmetry Ratio Matrix",
                 color="#ffffff", fontsize=11, pad=10)
    plt.tight_layout()
    return _b64(fig)


def chart_depletion(depletion_rows: list[dict], horizon: int = 90) -> str:
    """Bar chart: days-to-zero per system, coloured by status."""
    rows = [r for r in depletion_rows if r["days_to_zero"] != "∞"]
    if not rows:
        return ""
    labels = [r["system"] for r in rows]
    values = [float(r["days_to_zero"]) for r in rows]
    colours = [STATUS_COLOURS.get(r["status"], "#888") for r in rows]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.45)))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    ax.barh(labels, values, color=colours, edgecolor="#444", linewidth=0.4)
    ax.axvline(horizon, color="#ffffff", lw=1.0, ls="--",
               label=f"Two-war standard ({horizon} days)")
    ax.axvline(30, color="#fcbf49", lw=0.8, ls=":",
               label="30-day minimum threshold")

    ax.set_xlabel("Days to inventory zero (mean consumption)", color="#cccccc")
    ax.tick_params(colors="#cccccc", labelsize=8)
    ax.spines[:].set_color("#555")
    ax.invert_yaxis()

    status_patches = [mpatches.Patch(color=v, label=k)
                      for k, v in STATUS_COLOURS.items() if k != "SELF_SUSTAINING"]
    ax.legend(handles=status_patches + [
        mpatches.Patch(color="#ffffff", label=f"{horizon}-day standard (dashed)")],
        loc="lower right", facecolor="#2a2a3e", labelcolor="#cccccc", fontsize=7)
    ax.set_title("Figure 2 — Deterministic Two-War Inventory Depletion",
                 color="#ffffff", fontsize=11, pad=10)
    plt.tight_layout()
    return _b64(fig)


def chart_mc_coverage(coverage_dict: dict) -> str:
    """IQR box-plot style chart of days-of-coverage distribution."""
    keys   = list(coverage_dict.keys())
    medians = [coverage_dict[k].get("median_days", 0) for k in keys]
    p25s    = [coverage_dict[k].get("p25_days", 0)    for k in keys]
    p75s    = [coverage_dict[k].get("p75_days", 0)    for k in keys]

    fig, ax = plt.subplots(figsize=(10, max(4, len(keys) * 0.5)))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    y = np.arange(len(keys))
    ax.barh(y, p75s, left=p25s, height=0.5, color="#0f3460",
            edgecolor="#555", linewidth=0.4, label="IQR (P25–P75)")
    ax.scatter(medians, y, color="#00b4d8", s=40, zorder=5, label="Median")
    ax.axvline(90, color="#ffffff", lw=1.0, ls="--", label="90-day standard")
    ax.axvline(30, color="#fcbf49", lw=0.8, ls=":", label="30-day minimum")

    ax.set_yticks(y)
    ax.set_yticklabels(keys, fontsize=8)
    ax.set_xlabel("Days of coverage", color="#cccccc")
    ax.tick_params(colors="#cccccc")
    ax.spines[:].set_color("#555")
    ax.legend(loc="lower right", facecolor="#2a2a3e", labelcolor="#cccccc", fontsize=7)
    ax.set_title("Figure 3 — Monte Carlo Days-of-Coverage Distribution (IQR)",
                 color="#ffffff", fontsize=11, pad=10)
    plt.tight_layout()
    return _b64(fig)


def chart_marginal(marginal_rows: list[dict]) -> str:
    """Horizontal bar chart: coverage-days gained per $1B."""
    rows = [r for r in marginal_rows
            if isinstance(r.get("days_per_1000M"), (int, float))]
    if not rows:
        return ""
    labels  = [r["system"] for r in rows]
    values  = [r["days_per_1000M"] for r in rows]
    tier_c  = [TIER_COLOURS.get(r.get("tier", ""), "#888") for r in rows]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.45)))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    ax.barh(labels, values, color=tier_c, edgecolor="#444", linewidth=0.4)
    for i, (v, r) in enumerate(zip(values, rows)):
        ax.text(v + 0.5, i, f"{v:.0f}", va="center", fontsize=7, color="#cccccc")

    ax.set_xlabel("Coverage-days gained per $1B invested", color="#cccccc")
    ax.tick_params(colors="#cccccc", labelsize=8)
    ax.spines[:].set_color("#555")
    ax.invert_yaxis()

    tier_patches = [mpatches.Patch(color=v, label=k) for k, v in TIER_COLOURS.items()]
    ax.legend(handles=tier_patches, loc="lower right",
              facecolor="#2a2a3e", labelcolor="#cccccc", fontsize=7)
    ax.set_title("Figure 4 — Coverage-Days per $1B (Marginal Value Ranking)",
                 color="#ffffff", fontsize=11, pad=10)
    plt.tight_layout()
    return _b64(fig)


# ─────────────────────────────────────────────────────────────────────────────
# HTML report
# ─────────────────────────────────────────────────────────────────────────────

def generate_html(
    run_id: str,
    car_rows: list[dict],
    depletion_rows: list[dict],
    mc_results: dict,
    marginal_rows: list[dict],
    portfolio: dict,
    output_path: str,
    horizon: int = 90,
) -> str:
    """
    Render a self-contained HTML report and write it to output_path.
    Returns the output path.
    """
    log.info("Generating HTML report → %s", output_path)

    # Generate charts
    charts = {
        "car":      chart_car_matrix(car_rows),
        "depletion":chart_depletion(depletion_rows, horizon),
        "mc":       chart_mc_coverage(mc_results.get("coverage", {})),
        "marginal": chart_marginal(marginal_rows),
    }

    # Load Jinja2 template
    env = Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
    )
    try:
        tmpl = env.get_template("report.html")
    except Exception:
        log.warning("report.html template not found; using inline fallback")
        tmpl = None

    context = {
        "run_id":        run_id,
        "generated_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version":       __version__,
        "horizon":       horizon,
        "car_rows":      car_rows,
        "depletion_rows":depletion_rows,
        "mc_coverage":   mc_results.get("coverage", {}),
        "mc_readiness":  mc_results.get("readiness", {}),
        "marginal_rows": marginal_rows,
        "portfolio":     portfolio,
        "charts":        charts,
        "status_colours":STATUS_COLOURS,
    }

    if tmpl:
        html = tmpl.render(**context)
    else:
        html = _fallback_html(context)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    log.info("HTML report written: %d bytes", len(html))
    return output_path


def _fallback_html(ctx: dict) -> str:
    """Minimal inline HTML template used when Jinja template is unavailable."""
    def _img(b64):
        return f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:900px">' if b64 else ""

    rows_car = "".join(
        f"<tr><td>{r['label']}</td><td>${r['threat_cost']:,}</td>"
        f"<td>${r['defend_cost']:,}</td><td>{r['CAR_raw']:.4f}</td>"
        f"<td>{r['interpretation']}</td></tr>"
        for r in ctx["car_rows"]
    )
    rows_dep = "".join(
        f"<tr><td>{r['system']}</td><td>{r['inventory']:,}</td>"
        f"<td>{r['days_to_zero']}</td><td>{r['pct_at_horizon']}%</td>"
        f"<td>{r['status']}</td></tr>"
        for r in ctx["depletion_rows"]
    )
    rows_mc = "".join(
        f"<tr><td>{k}</td><td>{v.get('P_coverage',''):.1%}</td>"
        f"<td>{v.get('median_days','')}</td>"
        f"<td>{v.get('p25_days','')}–{v.get('p75_days','')}</td></tr>"
        for k, v in ctx["mc_coverage"].items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<title>CAS Report — {ctx['run_id']}</title>
<style>
  body{{font-family:sans-serif;background:#1e1e2e;color:#cdd6f4;margin:2rem}}
  h1{{color:#cba6f7}} h2{{color:#89b4fa;border-bottom:1px solid #444;padding-bottom:.3rem}}
  table{{border-collapse:collapse;width:100%;margin-bottom:2rem}}
  th{{background:#313244;padding:.5rem;text-align:left;font-size:.85rem}}
  td{{padding:.4rem .6rem;border-bottom:1px solid #313244;font-size:.82rem}}
  tr:hover td{{background:#252535}}
  .meta{{color:#a6adc8;font-size:.8rem;margin-bottom:2rem}}
  img{{display:block;margin:1rem 0;border:1px solid #444;border-radius:4px}}
</style></head>
<body>
<h1>Cost-Asymmetry Simulator — Run Report</h1>
<p class="meta">Run ID: {ctx['run_id']} &nbsp;|&nbsp;
Generated: {ctx['generated_at']} &nbsp;|&nbsp;
CAS v{ctx['version']} &nbsp;|&nbsp;
Horizon: {ctx['horizon']} days</p>

<h2>1. Cost Asymmetry Ratio Matrix</h2>
{_img(ctx['charts']['car'])}
<table><tr><th>Pairing</th><th>Threat $</th><th>Defense $</th>
<th>CAR</th><th>Status</th></tr>{rows_car}</table>

<h2>2. Two-War Inventory Depletion</h2>
{_img(ctx['charts']['depletion'])}
<table><tr><th>System</th><th>Inventory</th><th>Days→0</th>
<th>@ Horizon</th><th>Status</th></tr>{rows_dep}</table>

<h2>3. Monte Carlo Coverage Distribution</h2>
{_img(ctx['charts']['mc'])}
<table><tr><th>System</th><th>P(coverage)</th>
<th>Median Days</th><th>IQR</th></tr>{rows_mc}</table>

<h2>4. Marginal Value Analysis</h2>
{_img(ctx['charts']['marginal'])}

<h2>5. Portfolio Optimisation (${ctx['portfolio'].get('budget_B', 0):.1f}B)</h2>
<table><tr><th>System</th><th>Allocated $M</th><th>Final Median Days</th></tr>
{"".join(f"<tr><td>{s}</td><td>${ctx['portfolio']['allocation_M'].get(s,0):.0f}M</td><td>{ctx['portfolio']['final_days'].get(s,0):.0f}</td></tr>" for s in ctx['portfolio'].get('allocation_M',{}))}
</table>
</body></html>"""


# ─────────────────────────────────────────────────────────────────────────────
# PDF report (via FPDF2)
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(
    run_id: str,
    car_rows: list[dict],
    depletion_rows: list[dict],
    mc_results: dict,
    marginal_rows: list[dict],
    portfolio: dict,
    output_path: str,
    horizon: int = 90,
) -> str:
    """
    Render a PDF report with embedded charts.
    Returns the output path.
    """
    log.info("Generating PDF report → %s", output_path)

    # Save charts to temp PNG files
    import tempfile
    tmp_dir = tempfile.mkdtemp()
    chart_paths = {}
    for name, fn, args in [
        ("car",       chart_car_matrix,    (car_rows,)),
        ("depletion", chart_depletion,     (depletion_rows, horizon)),
        ("mc",        chart_mc_coverage,   (mc_results.get("coverage", {}),)),
        ("marginal",  chart_marginal,      (marginal_rows,)),
    ]:
        b64 = fn(*args)
        if b64:
            path = os.path.join(tmp_dir, f"{name}.png")
            with open(path, "wb") as fh:
                fh.write(base64.b64decode(b64))
            chart_paths[name] = path

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Cost-Asymmetry Simulator — Run Report", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6,
             f"Run: {run_id}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  "
             f"|  CAS v{__version__}  |  Horizon: {horizon} days",
             ln=True)
    pdf.ln(4)

    def _section(title, img_key, table_rows, col_headers):
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, title, ln=True)
        pdf.ln(2)
        if img_key in chart_paths:
            pdf.image(chart_paths[img_key], w=180)
            pdf.ln(3)
        if table_rows:
            pdf.set_font("Helvetica", "B", 7)
            col_w = 180 // len(col_headers)
            for h in col_headers:
                pdf.cell(col_w, 5, str(h)[:20], border=1)
            pdf.ln()
            pdf.set_font("Helvetica", "", 7)
            for row in table_rows[:20]:   # cap at 20 rows for PDF space
                for h in col_headers:
                    val = str(row.get(h, ""))[:20]
                    pdf.cell(col_w, 5, val, border=1)
                pdf.ln()
        pdf.ln(4)

    _section("1. Cost Asymmetry Ratio Matrix", "car", car_rows,
             ["label", "threat_cost", "defend_cost", "CAR_raw", "interpretation"])

    _section("2. Two-War Inventory Depletion", "depletion", depletion_rows,
             ["system", "inventory", "days_to_zero", "pct_at_horizon", "status"])

    mc_cov_rows = [{"system": k, **v}
                   for k, v in mc_results.get("coverage", {}).items()]
    _section("3. Monte Carlo Coverage", "mc", mc_cov_rows,
             ["system", "median_days", "p25_days", "p75_days"])

    _section("4. Marginal Value", "marginal", marginal_rows,
             ["system", "tier", "unit_cost", "days_per_100M", "days_per_1000M"])

    # Portfolio summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"5. Portfolio Optimisation (${portfolio.get('budget_B', 0):.1f}B)", ln=True)
    pdf.set_font("Helvetica", "", 8)
    for sys, alloc in portfolio.get("allocation_M", {}).items():
        fd = portfolio.get("final_days", {}).get(sys, 0)
        pdf.cell(0, 5,
                 f"  {sys:<20}  ${alloc:.0f}M  →  median {fd:.0f} days", ln=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    log.info("PDF report written: %s", output_path)
    return output_path
