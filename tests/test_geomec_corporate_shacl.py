"""Regression tests for SHACL shapes 23-30 (Geomech Corporate L6).

Run: python -m unittest tests.test_geomec_corporate_shacl
or:  python -m pytest tests/test_geomec_corporate_shacl.py

Verifies (1) the live module is conformant and (2) each shape fires on
deliberate violations — guards against accidental shape regressions.
"""
from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHAPES = ROOT / "data" / "geolytics-shapes.ttl"
DATA = ROOT / "data" / "geomechanics-corporate.json"

spec = importlib.util.spec_from_file_location(
    "geomec_ttl", ROOT / "scripts" / "geomec-corporate-to-ttl.py"
)
ttl_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ttl_mod)


def _validate(data_graph):
    import pyshacl
    from rdflib import Graph

    shapes_g = Graph().parse(SHAPES, format="turtle")
    conforms, results_g, _ = pyshacl.validate(
        data_graph=data_graph,
        shacl_graph=shapes_g,
        inference="rdfs",
        abort_on_first=False,
        allow_warnings=True,
    )
    from rdflib.namespace import RDF
    from rdflib import Namespace

    SH = Namespace("http://www.w3.org/ns/shacl#")
    msgs = []
    for v in results_g.subjects(RDF.type, SH.ValidationResult):
        msg = next(iter(results_g.objects(v, SH.resultMessage)), "")
        msgs.append(str(msg))
    return conforms, msgs


def _live_graph():
    from rdflib import Graph

    data_obj = json.loads(DATA.read_text(encoding="utf-8"))
    return Graph().parse(data=ttl_mod.emit(data_obj), format="turtle")


class TestLiveModuleConforms(unittest.TestCase):
    def test_live_module_is_conformant(self):
        conforms, msgs = _validate(_live_graph())
        self.assertTrue(conforms, f"Módulo L6 deveria estar conforme. Violações: {msgs}")


class TestShapesFireOnViolations(unittest.TestCase):
    """Each test mutates the live graph minimally and asserts the expected shape fires."""

    def setUp(self):
        from rdflib import Namespace

        self.GEO = Namespace("https://geolytics.petrobras.com.br/dict/")
        self.g = _live_graph()

    def test_shape23_bad_category(self):
        from rdflib import Literal

        self.g.remove((self.GEO.GEOMEC036, self.GEO.category, Literal("Formula")))
        self.g.add((self.GEO.GEOMEC036, self.GEO.category, Literal("BogusCategory")))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("category" in m.lower() for m in msgs))

    def test_shape23_bad_confidence(self):
        from rdflib import Literal

        self.g.remove((self.GEO.GEOMEC037, self.GEO.confidence, Literal("low")))
        self.g.add((self.GEO.GEOMEC037, self.GEO.confidence, Literal("ultra-low")))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("confidence" in m.lower() for m in msgs))

    def test_shape24_bad_relation_type_casing(self):
        """Lowercase or non-canonical verbs must be rejected by the sh:in enum."""
        from rdflib import BNode, Literal
        from rdflib.namespace import RDF

        bn = BNode()
        self.g.add((self.GEO.GEOMEC036, self.GEO.hasRelation, bn))
        self.g.add((bn, RDF.type, self.GEO.GeomechCorporateRelation))
        self.g.add((bn, self.GEO.relationType, Literal("is_part_of")))  # lowercase, not in enum
        self.g.add((bn, self.GEO.targetEntity, self.GEO.GEOMEC003))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("enum corporativo aprovado" in m for m in msgs),
                        f"Expected enum-rejection message, got: {msgs}")

    def test_shape25_low_confidence_without_gap_fires(self):
        """If a low-confidence entity loses its gaps it must fail."""
        from rdflib import Literal

        # GEOMEC037 has confidence=low; remove all evidence_gaps
        for o in list(self.g.objects(self.GEO.GEOMEC037, self.GEO.evidenceGap)):
            self.g.remove((self.GEO.GEOMEC037, self.GEO.evidenceGap, o))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("evidenceGap" in m or "evidence_gap" in m for m in msgs))

    def test_shape26_deprecated_without_replacedby_fires(self):
        # GEOMEC026 is deprecated — strip its replacedBy and confirm shape 26 fires
        for o in list(self.g.objects(self.GEO.GEOMEC026, self.GEO.replacedBy)):
            self.g.remove((self.GEO.GEOMEC026, self.GEO.replacedBy, o))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("replacedBy" in m for m in msgs))

    def test_shape27_active_ref_to_deprecated_fires(self):
        from rdflib import BNode, Literal
        from rdflib.namespace import RDF

        bn = BNode()
        self.g.add((self.GEO.GEOMEC035, self.GEO.hasRelation, bn))
        self.g.add((bn, RDF.type, self.GEO.GeomechCorporateRelation))
        self.g.add((bn, self.GEO.relationType, Literal("PRODUCES")))
        self.g.add((bn, self.GEO.targetEntity, self.GEO.GEOMEC026))  # deprecated
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("depreciada" in m for m in msgs))

    def test_shape28_formula_without_expression_fires(self):
        # Strip formulaExpression from GEOMEC036 (Formula category)
        for o in list(self.g.objects(self.GEO.GEOMEC036, self.GEO.formulaExpression)):
            self.g.remove((self.GEO.GEOMEC036, self.GEO.formulaExpression, o))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("formulaExpression" in m for m in msgs))

    def test_shape29_dangling_target_fires(self):
        from rdflib import BNode, Literal
        from rdflib.namespace import RDF

        bn = BNode()
        self.g.add((self.GEO.GEOMEC035, self.GEO.hasRelation, bn))
        self.g.add((bn, RDF.type, self.GEO.GeomechCorporateRelation))
        self.g.add((bn, self.GEO.relationType, Literal("INFLUENCES")))
        self.g.add((bn, self.GEO.targetEntity, self.GEO.GEOMEC999))  # nonexistent
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("GeomechCorporateEntity declarada" in m for m in msgs))

    def test_shape30_outofscope_without_module_fires(self):
        # GEOMEC026A has out_of_scope_flag — strip inScopeForModule
        for o in list(self.g.objects(self.GEO.GEOMEC026A, self.GEO.inScopeForModule)):
            self.g.remove((self.GEO.GEOMEC026A, self.GEO.inScopeForModule, o))
        conforms, msgs = _validate(self.g)
        self.assertFalse(conforms)
        self.assertTrue(any("inScopeForModule" in m for m in msgs))


if __name__ == "__main__":
    unittest.main()
