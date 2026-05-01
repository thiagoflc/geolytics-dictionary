#!/usr/bin/env python3
"""
report.py — Generate eval/results/report.md comparing all runners.

Reads the latest result file per runner from eval/results/, then writes
a Markdown comparison table with scores and deltas.

Usage:
    python3 eval/report.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"
REPORT_PATH = RESULTS_DIR / "report.md"

RUNNERS = ("vector_only", "graphrag", "graphrag_validator")

METRIC_LABELS = {
    "entity_recall": "Entity Recall (higher=better)",
    "fact_coverage": "Fact Coverage (higher=better)",
    "must_not_say_violations": "MustNotSay Violations (lower=better)",
    "validation_pass_rate": "Validation Pass Rate (higher=better)",
    "composite_score": "Composite Score (higher=better)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def latest_result(runner: str) -> dict | None:
    """Return the most recent result dict for a runner, or None."""
    pattern = f"{runner}-*.json"
    files = sorted(RESULTS_DIR.glob(pattern))
    if not files:
        return None
    with files[-1].open(encoding="utf-8") as fh:
        return json.load(fh)


def fmt(value: float | None, invert: bool = False) -> str:
    if value is None:
        return "n/a"
    display = (1.0 - value) if invert else value
    return f"{display:.4f}"


def delta_str(a: float | None, b: float | None, invert: bool = False) -> str:
    """Return delta string: b - a, formatted with sign."""
    if a is None or b is None:
        return "n/a"
    da = (1.0 - a) if invert else a
    db = (1.0 - b) if invert else b
    diff = db - da
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.4f}"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate() -> str:
    results: dict[str, dict | None] = {}
    for runner in RUNNERS:
        results[runner] = latest_result(runner)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []

    lines.append("# Eval Harness Report")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    # Summary table
    available = [r for r in RUNNERS if results[r] is not None]
    if not available:
        lines.append("No result files found. Run `python3 eval/run.py` first.")
        return "\n".join(lines)

    lines.append("## Summary")
    lines.append("")

    # Header
    header_cols = ["Metric"] + [r.replace("_", " ").title() for r in available]
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(header_cols)) + " |")

    invert_map: dict[str, bool] = {}  # no inversion — all metrics shown as stored

    for metric_key, metric_label in METRIC_LABELS.items():
        invert = invert_map.get(metric_key, False)
        row = [metric_label]
        for runner in available:
            scores = results[runner]["scores"]
            raw = scores.get(metric_key)
            row.append(fmt(raw, invert=invert))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")

    # Per-runner metadata
    lines.append("## Runner Details")
    lines.append("")
    for runner in available:
        r = results[runner]
        lines.append(f"### {runner}")
        lines.append("")
        lines.append(f"- Timestamp: {r['timestamp']}")
        lines.append(f"- Questions evaluated: {r['n_questions']}")
        cs = r['scores'].get('composite_score', 0)
        lines.append(f"- Composite score: {cs:.4f}")
        lines.append("")

    # Delta table (vs vector_only as baseline)
    if "vector_only" in available and len(available) > 1:
        lines.append("## Deltas vs vector_only")
        lines.append("")
        others = [r for r in available if r != "vector_only"]
        header_cols2 = ["Metric"] + [r.replace("_", " ").title() for r in others]
        lines.append("| " + " | ".join(header_cols2) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_cols2)) + " |")

        base_scores = results["vector_only"]["scores"]
        for metric_key, metric_label in METRIC_LABELS.items():
            invert = invert_map.get(metric_key, False)
            row = [metric_label]
            for runner in others:
                scores = results[runner]["scores"]
                row.append(delta_str(
                    base_scores.get(metric_key),
                    scores.get(metric_key),
                    invert=invert,
                ))
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    # Per-category breakdown for the best runner (graphrag_validator preferred)
    best_runner = "graphrag_validator" if "graphrag_validator" in available else available[-1]
    best_data = results[best_runner]
    if best_data and best_data.get("per_question"):
        lines.append(f"## Category Breakdown ({best_runner})")
        lines.append("")
        category_scores: dict[str, list[float]] = {}
        for pq in best_data["per_question"]:
            cat = pq.get("category", "unknown")
            category_scores.setdefault(cat, []).append(pq.get("composite_score", 0.0))

        lines.append("| Category | N | Avg Composite |")
        lines.append("| --- | --- | --- |")
        for cat in sorted(category_scores):
            vals = category_scores[cat]
            avg = sum(vals) / len(vals)
            lines.append(f"| {cat} | {len(vals)} | {avg:.4f} |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    report_text = generate()
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print(f"Report written to: {REPORT_PATH}")
    print()
    print(report_text)


if __name__ == "__main__":
    main()
