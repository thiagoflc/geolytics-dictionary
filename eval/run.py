#!/usr/bin/env python3
"""
run.py — CLI entry point for the geobrain eval harness.

Usage:
    python3 eval/run.py --runner vector_only --offline --limit 30
    python3 eval/run.py --runner graphrag --offline --limit 30
    python3 eval/run.py --runner graphrag_validator --offline --limit 30

Results are written to eval/results/<runner>-<timestamp>.json.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the project root is on the path so imports work regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from eval.metrics import score_answer, aggregate  # noqa: E402

GOLDEN_SET = PROJECT_ROOT / "eval" / "golden-set.jsonl"
RESULTS_DIR = PROJECT_ROOT / "eval" / "results"
VALID_RUNNERS = ("vector_only", "graphrag", "graphrag_validator")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_golden_set(path: Path, limit: int | None) -> list[dict]:
    questions: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    if limit:
        questions = questions[:limit]
    return questions


def load_runner(name: str):
    if name not in VALID_RUNNERS:
        raise ValueError(f"Unknown runner '{name}'. Valid: {VALID_RUNNERS}")
    module = importlib.import_module(f"eval.runners.{name}")
    return module


def run_question(runner_module, question_row: dict) -> dict:
    """Run the runner on one question and return a per-question result dict."""
    question_text = question_row.get("question_pt", "")
    try:
        answer = runner_module.run(question_text)
        answer_text = answer.text
        entities_cited = answer.entities_cited
        validations = answer.validations
        error = None
    except Exception as exc:
        answer_text = ""
        entities_cited = []
        validations = []
        error = str(exc)

    scores = score_answer(question_row, answer_text, validations, entities_cited)

    return {
        "id": question_row.get("id", ""),
        "category": question_row.get("category", ""),
        "difficulty": question_row.get("difficulty", ""),
        "question_pt": question_row.get("question_pt", ""),
        "answer_text": answer_text[:500],  # truncate for result file size
        "entities_cited": entities_cited,
        "n_validations_violated": len(validations),
        "error": error,
        **scores,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the geobrain eval harness."
    )
    parser.add_argument(
        "--runner",
        required=True,
        choices=VALID_RUNNERS,
        help="Which runner to use.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        default=True,
        help="Offline mode — no network calls (default: True).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit evaluation to the first N questions.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    questions = load_golden_set(GOLDEN_SET, args.limit)
    print(f"Loaded {len(questions)} questions from golden set.")

    runner = load_runner(args.runner)
    print(f"Runner: {args.runner}")

    per_question: list[dict] = []
    for i, q in enumerate(questions, 1):
        print(f"  [{i}/{len(questions)}] {q.get('id', '?')} ({q.get('category', '?')})", end=" ... ", flush=True)
        result = run_question(runner, q)
        per_question.append(result)
        print(f"composite={result['composite_score']:.3f}")

    scores = aggregate(per_question)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RESULTS_DIR / f"{args.runner}-{timestamp}.json"

    output = {
        "runner": args.runner,
        "timestamp": timestamp,
        "n_questions": len(per_question),
        "scores": scores,
        "per_question": per_question,
    }

    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(output, fh, ensure_ascii=False, indent=2)

    print(f"\nResults written to: {out_path}")
    print("\nAggregate scores:")
    for k, v in scores.items():
        print(f"  {k}: {v:.4f}")


if __name__ == "__main__":
    main()
