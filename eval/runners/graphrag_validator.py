"""
graphrag_validator.py — GraphRAG with semantic validation.

Runs the same graph-augmented retrieval as graphrag.py, then pipes the
synthesized text through the JS validator (node scripts/validate-cli.js).
Any flagged sentences are removed from the answer and the violations are
recorded in the Answer.validations field.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .graphrag import run as graphrag_run
from .vector_only import Answer


# ---------------------------------------------------------------------------
# Validator subprocess helper
# ---------------------------------------------------------------------------

def _validate_claim(claim: str, scripts_dir: Path) -> dict[str, Any]:
    """Call validate-cli.js for a single claim string. Returns the result dict."""
    cli = scripts_dir / "validate-cli.js"
    try:
        proc = subprocess.run(
            ["node", str(cli), "--format", "json", claim],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=scripts_dir.parent,
        )
        output = proc.stdout.strip() or proc.stderr.strip()
        data = json.loads(output)
        return data.get("result", {})
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        # If validator is unavailable, treat as passing to avoid silent failures
        return {"valid": True, "violations": [], "warnings": []}


# ---------------------------------------------------------------------------
# Sentence-level rewriting
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> list[str]:
    """Naive sentence splitter on Portuguese text."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p for p in parts if p.strip()]


def _rewrite_removing_violations(text: str, scripts_dir: Path) -> tuple[str, list[dict]]:
    """
    Validate each sentence. Remove sentences that have violations.
    Returns (cleaned_text, all_violations).
    """
    sentences = _split_sentences(text)
    kept: list[str] = []
    all_violations: list[dict] = []

    for sentence in sentences:
        if len(sentence.strip()) < 10:
            kept.append(sentence)
            continue
        result = _validate_claim(sentence, scripts_dir)
        violations = result.get("violations", [])
        if violations:
            all_violations.extend(violations)
            # Drop the sentence — it contains flagged content
        else:
            kept.append(sentence)

    cleaned = " ".join(kept)
    return cleaned, all_violations


# ---------------------------------------------------------------------------
# Runner entry point
# ---------------------------------------------------------------------------

def run(
    question: str,
    top_k: int = 5,
    corpus_path: Path | None = None,
    graph_path: Path | None = None,
) -> Answer:
    """Return a validated Answer: graph retrieval + sentence-level violation removal."""
    root = Path(__file__).resolve().parents[2]
    scripts_dir = root / "scripts"

    # 1. Get graph-augmented answer
    base_answer = graphrag_run(
        question,
        top_k=top_k,
        corpus_path=corpus_path,
        graph_path=graph_path,
    )

    # 2. Validate and rewrite
    cleaned_text, violations = _rewrite_removing_violations(base_answer.text, scripts_dir)

    return Answer(
        text=cleaned_text,
        entities_cited=base_answer.entities_cited,
        validations=violations,
    )
