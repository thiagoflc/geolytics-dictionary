"""Regression tests for SHACL shapes — 6-layer ontology model invariants.

Run: python -m unittest tests.test_ontology_layers_shacl
or:  python -m pytest tests/test_ontology_layers_shacl.py

Verifies (1) the live graph data/geobrain.ttl conforms to
data/ontology-layers-shapes.ttl, and (2) each shape fires on deliberate
violations injected into a minimal synthetic graph (kept tiny so the
SPARQL-based shapes finish in a few seconds rather than the ~65s a full
geobrain.ttl validation takes).

Lives in tests/ (repo root), not python/tests/, because it is a live-data
integration test — kept out of the python SDK test suite that runs in the
test-python.yml matrix. Run on demand or as part of validate-ontology.yml.

Mirrors the style of tests/test_geomec_corporate_shacl.py.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_TTL = ROOT / "data" / "geobrain.ttl"
SHAPES = ROOT / "data" / "ontology-layers-shapes.ttl"
ENTITY_GRAPH_JSON = ROOT / "data" / "entity-graph.json"

GEO_NS = "https://geolytics.petrobras.com.br/dict/"


def _validate(data_graph):
    """Run pyshacl validation against ontology-layers-shapes.ttl.

    Returns (conforms, results_graph, findings_list).
    """
    import pyshacl
    from rdflib import Graph, Namespace
    from rdflib.namespace import RDF

    shapes_g = Graph().parse(str(SHAPES), format="turtle")
    conforms, results_g, _ = pyshacl.validate(
        data_graph=data_graph,
        shacl_graph=shapes_g,
        inference=None,
        abort_on_first=False,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        js=False,
    )
    SH = Namespace("http://www.w3.org/ns/shacl#")
    findings = []
    for v in results_g.subjects(RDF.type, SH.ValidationResult):
        sev = next(iter(results_g.objects(v, SH.resultSeverity)), None)
        msg = next(iter(results_g.objects(v, SH.resultMessage)), "")
        focus = next(iter(results_g.objects(v, SH.focusNode)), "")
        source = next(iter(results_g.objects(v, SH.sourceShape)), "")
        findings.append(
            {
                "severity": str(sev) if sev else "",
                "message": str(msg),
                "focus": str(focus),
                "source": str(source),
            }
        )
    return conforms, results_g, findings


def _violations(findings):
    return [f for f in findings if f["severity"].endswith("#Violation")]


def _warnings(findings):
    return [f for f in findings if f["severity"].endswith("#Warning")]


def _make_synthetic_graph():
    """Build a tiny graph with anchor nodes for cross-references.

    Includes one node per role used in the shapes' target conditions so
    synthetic violations can reference well_anchor / well_operation /
    artifact_primary nodes. Keeps SHACL validation fast (~1s) versus
    ~65s for a full geobrain.ttl validation.
    """
    from rdflib import Graph, Literal, Namespace

    geo = Namespace(GEO_NS)
    g = Graph()
    g.bind("geo", geo)

    # Anchors used by other shapes when they need a target with a known role.
    anchors = {
        "anchor-well": "well_anchor",
        "anchor-op": "well_operation",
        "anchor-art": "artifact_primary",
    }
    for nid, role in anchors.items():
        n = geo[nid]
        g.add((n, geo.entityType, Literal("operational")))
        g.add((n, geo.ontologicalRole, Literal(role)))

    return g


class TestLiveGraphConforms(unittest.TestCase):
    """The live graph must pass with zero hard Violations.

    Warnings are expected and tracked separately — they map to F4/F7 work.
    Run is class-level (setUpClass) because pyshacl is slow on geobrain.ttl.
    """

    @classmethod
    def setUpClass(cls):
        from rdflib import Graph

        live = Graph().parse(str(DATA_TTL), format="turtle")
        cls.conforms, _, cls.findings = _validate(live)

    def test_live_graph_conforms(self):
        viols = _violations(self.findings)
        self.assertEqual(
            len(viols),
            0,
            f"Live graph should have 0 Violations. Got {len(viols)}: "
            + "; ".join(f["message"][:120] for f in viols[:5]),
        )
        # Warnings are allowed; conforms must be True (allow_warnings=True
        # makes pyshacl return True even with sh:Warning results).
        self.assertTrue(self.conforms, "Live graph should conform (warnings allowed)")

    def test_live_graph_has_only_warnings(self):
        """Smoke test: any non-conformance is at most Warning severity."""
        non_warning = [
            f
            for f in self.findings
            if f["severity"] and not f["severity"].endswith("#Warning")
        ]
        self.assertEqual(
            len(non_warning),
            0,
            f"Non-warning findings: {[(f['severity'], f['message'][:80]) for f in non_warning[:5]]}",
        )


class TestNoBannedPredicates(unittest.TestCase):
    """No related_to anywhere; used_with is tracked as Warning until F4."""

    @classmethod
    def setUpClass(cls):
        from rdflib import Graph

        cls.live = Graph().parse(str(DATA_TTL), format="turtle")

    def test_no_related_to(self):
        from rdflib import URIRef

        related_to = URIRef(GEO_NS + "related_to")
        triples = list(self.live.triples((None, related_to, None)))
        self.assertEqual(
            len(triples),
            0,
            f"Predicate geo:related_to is banned (docs/ONTOLOGY_PREDICATES.md §5). "
            f"Found {len(triples)} occurrences in data/geobrain.ttl.",
        )


class TestAllNodesHaveRole(unittest.TestCase):
    """100% role coverage on the entity-graph JSON source-of-truth."""

    def test_all_nodes_have_ontological_role(self):
        data = json.loads(ENTITY_GRAPH_JSON.read_text(encoding="utf-8"))
        nodes = data["nodes"]
        missing = [n["id"] for n in nodes if not n.get("ontological_role")]
        self.assertEqual(
            len(missing),
            0,
            f"All nodes must declare ontological_role. Missing on: {missing[:10]}",
        )


class TestRoleValuesCanonical(unittest.TestCase):
    """Every ontological_role value must be in the canonical 19-set."""

    CANONICAL = frozenset(
        [
            "well_anchor",
            "well_operation",
            "artifact_primary",
            "feature_observation",
            "interpretation_process",
            "engineering_artifact",
            "regulatory_anchor",
            "organizational_actor",
            "domain_anchor",
            "well_attribute_concept",
            "equipment",
            "governance_artifact",
            "kpi_metric",
            "lifecycle_state",
            "lifecycle_outcome",
            "dataset_concept",
            "signal_concept",
            "event_observation",
            "unclassified",
        ]
    )

    def test_role_values_canonical(self):
        data = json.loads(ENTITY_GRAPH_JSON.read_text(encoding="utf-8"))
        nodes = data["nodes"]
        non_canonical = [
            (n["id"], n.get("ontological_role"))
            for n in nodes
            if n.get("ontological_role") not in self.CANONICAL
        ]
        self.assertEqual(
            len(non_canonical),
            0,
            f"All ontological_role values must be in the canonical 19-set. "
            f"Non-canonical found: {non_canonical[:10]}",
        )


class TestShapesFireOnViolations(unittest.TestCase):
    """For each shape, inject a synthetic violation into a tiny graph and
    assert the shape fires.

    Uses a small synthetic graph (not data/geobrain.ttl) to keep each test
    under a few seconds — pyshacl SPARQL constraints are O(N) over the
    target set.
    """

    def setUp(self):
        from rdflib import Namespace

        self.GEO = Namespace(GEO_NS)
        self.g = _make_synthetic_graph()

    # ── Shape 1: well_anchor cannot have joined_by_modules ────────────────
    def test_shape1_well_anchor_with_joined_by_modules_fires(self):
        from rdflib import Literal

        self.g.add((self.GEO["anchor-well"], self.GEO.joinedByModules, Literal("OGEOMEC")))
        _, _, findings = _validate(self.g)
        viols = _violations(findings)
        self.assertTrue(
            any(
                "Anti-padrão Q7" in f["message"] or "joinedByModules" in f["message"]
                for f in viols
            ),
            f"Shape 1 should fire on well_anchor + joined_by_modules. "
            f"Violations: {[f['message'][:80] for f in viols]}",
        )

    # ── Shape 2: interpretation_process needs input/output edges ──────────
    def test_shape2_interpretation_without_io_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-interp-no-io"]
        self.g.add((synth, self.GEO.entityType, Literal("analytical")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("interpretation_process")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        # Shape 2 has TWO SPARQL constraints (input + output), so an isolated
        # interp_process should fire at least one (typically both).
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 2 should fire on isolated interpretation_process. "
            f"Got {len(synth_warns)} warnings on synth node",
        )

    # ── Shape 3: engineering_artifact needs applies_to/supports/constrains ──
    def test_shape3_engineering_artifact_floating_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-eng-floating"]
        self.g.add((synth, self.GEO.entityType, Literal("operational")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("engineering_artifact")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 3 should fire on floating engineering_artifact",
        )

    # ── Shape 4: feature_observation must anchor ──────────────────────────
    def test_shape4_unanchored_feature_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-feature-unanchored"]
        self.g.add((synth, self.GEO.entityType, Literal("geological")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("feature_observation")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 4 should fire on unanchored feature_observation",
        )

    # ── Shape 5: artifact_primary must trace to operation ─────────────────
    def test_shape5_orphan_artifact_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-orphan-artifact"]
        self.g.add((synth, self.GEO.entityType, Literal("analytical")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("artifact_primary")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 5 should fire on orphan artifact_primary",
        )

    # ── Shape 6a: related_to is banned ────────────────────────────────────
    def test_shape6a_related_to_fires(self):
        bad = self.GEO["synthetic-bad-related-to"]
        self.g.add((bad, self.GEO.related_to, self.GEO["anchor-well"]))
        _, _, findings = _validate(self.g)
        viols = _violations(findings)
        self.assertTrue(
            any("related_to" in f["message"] or "banido" in f["message"] for f in viols),
            f"Shape 6a should fire on geo:related_to. "
            f"Violations: {[f['message'][:80] for f in viols]}",
        )

    # ── Shape 6b: used_with is deprecated (Warning) ───────────────────────
    def test_shape6b_used_with_fires_as_warning(self):
        bad = self.GEO["synthetic-bad-used-with"]
        self.g.add((bad, self.GEO.used_with, self.GEO["anchor-well"]))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        viols = _violations(findings)
        self.assertTrue(
            any("used_with" in f["message"] for f in warns),
            f"Shape 6b should fire on geo:used_with as Warning",
        )
        self.assertFalse(
            any("used_with" in f["message"] for f in viols),
            "used_with should be Warning, not Violation",
        )

    # ── Shape 7: every node must declare ontological_role ─────────────────
    def test_shape7_node_without_role_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-node-no-role"]
        # Has entityType (so it's targeted by sh:targetSubjectsOf geo:entityType)
        # but lacks ontologicalRole.
        self.g.add((synth, self.GEO.entityType, Literal("operational")))
        _, _, findings = _validate(self.g)
        viols = _violations(findings)
        synth_viols = [v for v in viols if str(synth) == v["focus"]]
        self.assertGreaterEqual(
            len(synth_viols),
            1,
            f"Shape 7 should fire on a node missing ontologicalRole",
        )

    # ── Shape 8: ontological_role must be canonical ───────────────────────
    def test_shape8_non_canonical_role_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-bad-role"]
        self.g.add((synth, self.GEO.entityType, Literal("operational")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("not_a_canonical_role")))
        _, _, findings = _validate(self.g)
        viols = _violations(findings)
        synth_viols = [v for v in viols if str(synth) == v["focus"]]
        self.assertTrue(
            any("canônico" in v["message"] or "canonical" in v["message"] for v in synth_viols),
            f"Shape 8 should fire with canonical-set message. "
            f"Got: {[v['message'][:80] for v in synth_viols]}",
        )

    # ── Shape 9: well_operation should have actor or location ─────────────
    def test_shape9_operation_without_actor_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-op-no-actor"]
        self.g.add((synth, self.GEO.entityType, Literal("operational")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("well_operation")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 9 should fire on well_operation lacking actor/location",
        )

    # ── Shape 10: domain_anchor should classify something ─────────────────
    def test_shape10_domain_anchor_without_children_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-empty-domain"]
        self.g.add((synth, self.GEO.entityType, Literal("operational")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("domain_anchor")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 10 should fire on a domain_anchor with no inbound is_part_of",
        )

    # ── Shape 11: dataset_concept should reference origin ─────────────────
    def test_shape11_dataset_without_origin_fires(self):
        from rdflib import Literal

        synth = self.GEO["synthetic-dataset-no-origin"]
        self.g.add((synth, self.GEO.entityType, Literal("analytical")))
        self.g.add((synth, self.GEO.ontologicalRole, Literal("dataset_concept")))
        _, _, findings = _validate(self.g)
        warns = _warnings(findings)
        synth_warns = [w for w in warns if str(synth) == w["focus"]]
        self.assertGreaterEqual(
            len(synth_warns),
            1,
            f"Shape 11 should fire on a dataset_concept with no references/stored_in",
        )


if __name__ == "__main__":
    unittest.main()
