"""
metrics.py — Evaluation metrics for the geolytics-dictionary eval harness.

All functions operate on plain Python dicts/lists so they can be called
from run.py without additional dependencies.
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Individual metrics
# ---------------------------------------------------------------------------

def entity_recall(
    expected_entities: list[str],
    cited_entities: list[str],
) -> float:
    """Fraction of expected entities found in the cited set (case-insensitive)."""
    if not expected_entities:
        return 1.0
    cited_lower = {e.lower() for e in cited_entities}
    hits = sum(1 for e in expected_entities if e.lower() in cited_lower)
    return hits / len(expected_entities)


def fact_coverage(
    expected_facts: list[str],
    answer_text: str,
) -> float:
    """Fraction of expected fact tokens present in the answer (case-insensitive)."""
    if not expected_facts:
        return 1.0
    answer_lower = answer_text.lower()
    hits = 0
    for fact in expected_facts:
        # Check if any word of the fact appears in the answer
        words = [w for w in fact.lower().split() if len(w) > 3]
        if not words:
            words = fact.lower().split()
        if any(w in answer_lower for w in words):
            hits += 1
    return hits / len(expected_facts)


def must_not_say_violations(
    must_not_say: list[str],
    answer_text: str,
) -> float:
    """
    Rate of forbidden phrases present in the answer.
    Returns 0.0 (no violations) to 1.0 (all forbidden phrases present).
    """
    if not must_not_say:
        return 0.0
    answer_lower = answer_text.lower()
    hits = sum(1 for phrase in must_not_say if phrase.lower() in answer_lower)
    return hits / len(must_not_say)


def validation_pass_rate(validations: list[dict[str, Any]]) -> float:
    """
    1.0 if no validation violations, otherwise fraction of sentences without violations.
    validations is a flat list of violation dicts (empty = all passed).
    """
    # Each item in validations is a violation; empty list = clean
    # We treat 0 violations as 1.0 and scale down by violation count relative to
    # a ceiling of 10 violations (heuristic for normalisation).
    if not validations:
        return 1.0
    n_violations = len(validations)
    # Cap at 10 so the metric stays in [0, 1]
    return max(0.0, 1.0 - n_violations / 10.0)


def composite_score(
    er: float,
    fc: float,
    mns: float,
    vpr: float,
) -> float:
    """
    Weighted composite:
      0.35 * entity_recall
    + 0.35 * fact_coverage
    + 0.20 * (1 - must_not_say_violations_rate)
    + 0.10 * validation_pass_rate
    """
    return 0.35 * er + 0.35 * fc + 0.20 * (1.0 - mns) + 0.10 * vpr


# ---------------------------------------------------------------------------
# Aggregate helpers
# ---------------------------------------------------------------------------

def aggregate(per_question: list[dict[str, Any]]) -> dict[str, float]:
    """Compute mean of each metric across all per-question results."""
    if not per_question:
        return {
            "entity_recall": 0.0,
            "fact_coverage": 0.0,
            "must_not_say_violations": 0.0,
            "validation_pass_rate": 0.0,
            "composite_score": 0.0,
        }

    keys = ["entity_recall", "fact_coverage", "must_not_say_violations",
            "validation_pass_rate", "composite_score"]
    totals = {k: 0.0 for k in keys}
    for row in per_question:
        for k in keys:
            totals[k] += row.get(k, 0.0)
    n = len(per_question)
    return {k: totals[k] / n for k in keys}


def score_answer(question_row: dict[str, Any], answer_text: str, validations: list[dict], cited_entities: list[str]) -> dict[str, float]:
    """Compute all metrics for a single question and return a scores dict."""
    er = entity_recall(question_row.get("expected_entities", []), cited_entities)
    fc = fact_coverage(question_row.get("expected_facts", []), answer_text)
    mns = must_not_say_violations(question_row.get("must_not_say", []), answer_text)
    vpr = validation_pass_rate(validations)
    cs = composite_score(er, fc, mns, vpr)
    return {
        "entity_recall": er,
        "fact_coverage": fc,
        "must_not_say_violations": mns,
        "validation_pass_rate": vpr,
        "composite_score": cs,
    }
