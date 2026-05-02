"""cli.py — Command-line interface for geobrain.

Entry point: ``geolytics-validate``

Usage::

    geolytics-validate "Reserva 4P do Campo de Búzios"
    geolytics-validate --json "Bloco BS-500 em regime de Privatização"
    echo "text to validate" | geolytics-validate -
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import NoReturn


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="geolytics-validate",
        description=(
            "Semantic validator for Geolytics O&G domain claims. "
            "Validates free-text or structured claims against canonical "
            "SPE-PRMS categories, ANP well codes, regime contratual, and more."
        ),
    )
    p.add_argument(
        "claim",
        nargs="?",
        help=(
            "Text claim to validate. Use '-' to read from stdin. "
            "If omitted, reads from stdin."
        ),
    )
    p.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        default=False,
        help="Output the full validation report as JSON.",
    )
    p.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Print the package version and exit.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.version:
        from geobrain._version import __version__
        print(__version__)
        return 0

    # Read claim
    if args.claim is None or args.claim == "-":
        claim_text = sys.stdin.read().strip()
    else:
        claim_text = args.claim.strip()

    if not claim_text:
        parser.error("No claim provided. Pass text as argument or via stdin.")

    from geobrain.validator import Validator

    v = Validator()
    report = v.validate(claim_text)

    if args.output_json:
        output = {
            "valid": report.valid,
            "violations": [
                {
                    "rule": viol.rule,
                    "severity": viol.severity,
                    "evidence": viol.evidence,
                    "suggested_fix": viol.suggested_fix,
                    "source_layer": viol.source_layer,
                }
                for viol in report.violations
            ],
            "warnings": [
                {
                    "rule": warn.rule,
                    "severity": warn.severity,
                    "evidence": warn.evidence,
                    "suggested_fix": warn.suggested_fix,
                    "source_layer": warn.source_layer,
                }
                for warn in report.warnings
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if report.valid and not report.warnings:
            print("OK — no violations found.")
        else:
            if report.violations:
                print(f"INVALID — {len(report.violations)} violation(s):")
                for viol in report.violations:
                    print(f"  [{viol.rule}] {viol.evidence}")
                    print(f"    Fix: {viol.suggested_fix}")
            if report.warnings:
                print(f"WARNINGS — {len(report.warnings)} warning(s):")
                for warn in report.warnings:
                    print(f"  [{warn.rule}] {warn.evidence}")
                    print(f"    Fix: {warn.suggested_fix}")

    return 0 if report.valid else 1


if __name__ == "__main__":
    sys.exit(main())
