#!/usr/bin/env python3
"""F5 audit — emits data/ontological_role_audit.json.

Reads data/entity-graph.json (already annotated by scripts/generate.js) and
writes a coverage report describing per-role counts, per-type x role
cross-tab, and the list of any nodes still flagged `unclassified`.

Run after `node scripts/generate.js`. The audit file is informational only;
it documents the current classifier output and is regenerated each run.

Usage: python3 scripts/audit-ontological-roles.py
"""
from __future__ import annotations

import json
import os
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "data", "entity-graph.json")
TARGET = os.path.join(ROOT, "data", "ontological_role_audit.json")

# Borderline / curator-review-worthy decisions. These are not errors —
# they are explicitly documented choices in the rule-based classifier
# (see scripts/generate.js inferOntologicalRole). Listed here so curators
# can revisit if domain conventions shift.
BORDERLINE_NOTES = [
    {
        "node_id": "wireline-logging",
        "decision": "well_operation",
        "alternative": "artifact_primary",
        "rationale": (
            "wireline-logging is treated as the L2 operation. The artifact "
            "produced is captured separately by perfil-poco / log-curve-type "
            "/ wireline-run."
        ),
    },
    {
        "node_id": "mudlogging-time-series",
        "decision": "artifact_primary",
        "alternative": "well_operation",
        "rationale": (
            "The data-series is the primary artifact (L3); the operation "
            "itself is `mudlogging` (separate node)."
        ),
    },
    {
        "node_id": "campo-tensional",
        "decision": "feature_observation",
        "alternative": "interpretation_process",
        "rationale": (
            "Stress field is treated as the OBSERVED state (L4), not the "
            "process that yields it."
        ),
    },
    {
        "node_id": "janela-lama",
        "decision": "engineering_artifact",
        "alternative": "feature_observation",
        "rationale": (
            "Mud window is the operational design output (L6), even though "
            "it is computed from observed pressure gradients."
        ),
    },
    {
        "node_id": "GEOMEC035",
        "decision": "interpretation_process",
        "alternative": "engineering_artifact",
        "rationale": (
            "3D reservoir geomechanical model is treated as the modelling "
            "process (L5), not the design artifact."
        ),
    },
    {
        "node_id": "GEOMEC084",
        "decision": "governance_artifact",
        "alternative": "interpretation_process",
        "rationale": (
            "WSM 2025 Quality Scheme is a quality framework / governance "
            "rubric, not the inversion process itself."
        ),
    },
    {
        "node_id": "seismic-acquisition-survey",
        "decision": "well_operation",
        "alternative": "artifact_primary",
        "rationale": (
            "Survey is the field acquisition program; the resulting dataset "
            "is downstream and not yet a separate node."
        ),
    },
    {
        "node_id": "GM027",
        "decision": "governance_artifact",
        "alternative": "interpretation_process",
        "rationale": (
            "LaudoGeomecanico is the deliverable report; the cognitive "
            "process upstream is GeomechanicalInterpretation."
        ),
    },
]


def main() -> int:
    with open(SOURCE, encoding="utf-8") as fh:
        graph = json.load(fh)

    nodes = graph["nodes"]
    total = len(nodes)
    missing = [n["id"] for n in nodes if "ontological_role" not in n]
    unclassified = [n["id"] for n in nodes if n.get("ontological_role") == "unclassified"]

    role_counts = defaultdict(int)
    role_to_ids = defaultdict(list)
    type_role = defaultdict(lambda: defaultdict(int))

    for n in nodes:
        role = n.get("ontological_role", "MISSING")
        role_counts[role] += 1
        role_to_ids[role].append(n["id"])
        type_role[n.get("type", "MISSING")][role] += 1

    # Sort distributions by count desc
    role_distribution = OrderedDict(
        sorted(role_counts.items(), key=lambda x: -x[1])
    )
    type_x_role = OrderedDict(
        (
            t,
            OrderedDict(sorted(roles.items(), key=lambda x: -x[1])),
        )
        for t, roles in sorted(type_role.items())
    )

    audit = OrderedDict(
        [
            ("schema_version", "1.0.0"),
            ("generated", datetime.now(timezone.utc).isoformat(timespec="seconds")),
            (
                "description",
                (
                    "F5 audit of `ontological_role` annotation across "
                    "data/entity-graph.json. Roles inferred by "
                    "scripts/generate.js inferOntologicalRole(); see "
                    "docs/ONTOLOGY_LAYERS.md §3 + §5 for the canonical role "
                    "vocabulary."
                ),
            ),
            (
                "totals",
                OrderedDict(
                    [
                        ("nodes", total),
                        ("annotated", total - len(missing)),
                        ("missing_field", len(missing)),
                        ("unclassified", len(unclassified)),
                        (
                            "unclassified_pct",
                            round(100.0 * len(unclassified) / total, 2)
                            if total
                            else 0,
                        ),
                    ]
                ),
            ),
            ("role_distribution", role_distribution),
            ("type_x_role", type_x_role),
            (
                "unclassified_nodes",
                [
                    OrderedDict(
                        [
                            ("id", n["id"]),
                            ("type", n.get("type")),
                            ("label", n.get("label")),
                        ]
                    )
                    for n in nodes
                    if n.get("ontological_role") == "unclassified"
                ],
            ),
            ("missing_field_nodes", missing),
            ("borderline_decisions", BORDERLINE_NOTES),
        ]
    )

    with open(TARGET, "w", encoding="utf-8") as fh:
        json.dump(audit, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"  total nodes:        {total}")
    print(f"  annotated:          {total - len(missing)}")
    print(f"  missing field:      {len(missing)}")
    print(f"  unclassified:       {len(unclassified)} "
          f"({audit['totals']['unclassified_pct']}%)")
    print()
    print("  role distribution:")
    for role, count in role_distribution.items():
        print(f"    {role:<28s} {count}")
    print()
    print(f"  audit written to: data/ontological_role_audit.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
