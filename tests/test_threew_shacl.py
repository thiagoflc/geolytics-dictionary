"""Regression tests for SHACL shapes 31-33 (Petrobras 3W).

Run: python -m pytest tests/test_threew_shacl.py -v

Verifies that each new 3W NodeShape accepts valid data and rejects
deliberate violations.
"""
from __future__ import annotations
import unittest
from pathlib import Path

try:
    import pyshacl
    from rdflib import Graph, Literal, URIRef, Namespace, BNode
    from rdflib.namespace import RDF, XSD
    PYSHACL_AVAILABLE = True
except ImportError:
    PYSHACL_AVAILABLE = False

ROOT = Path(__file__).resolve().parent.parent
SHAPES = ROOT / "data" / "geolytics-shapes.ttl"

GEO = Namespace("https://geolytics.petrobras.com.br/dict/")
THREEW = Namespace("https://github.com/petrobras/3W#")

PREFIXES = """
@prefix geo: <https://geolytics.petrobras.com.br/dict/> .
@prefix threew: <https://github.com/petrobras/3W#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


def _validate_ttl(ttl_str: str):
    """Parse Turtle string, validate against shapes, return (conforms, violations)."""
    data_g = Graph().parse(data=ttl_str, format="turtle")
    shapes_g = Graph().parse(SHAPES, format="turtle")
    conforms, results_g, _ = pyshacl.validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        inference="rdfs",
        abort_on_first=False,
        allow_warnings=True,
    )
    from rdflib.namespace import SH
    violations = list(results_g.subjects(RDF.type, SH.ValidationResult))
    return conforms, violations


@unittest.skipUnless(PYSHACL_AVAILABLE, "pyshacl not installed")
class TestOperationalEventShape(unittest.TestCase):
    """geo:OperationalEventShape — label 0-9 or transient {101,102,105-109}."""

    VALID_TTL = PREFIXES + """
geo:event_severe_slugging a geo:OperationalEvent ;
    geo:threewLabel 3 ;
    geo:label "Severe Slugging" .
"""

    INVALID_LABEL_TTL = PREFIXES + """
geo:event_bad a geo:OperationalEvent ;
    geo:threewLabel 99 ;
    geo:label "Bad Event" .
"""

    INVALID_TRANSIENT_TTL = PREFIXES + """
geo:event_bad_transient a geo:OperationalEvent ;
    geo:threewLabel 103 ;
    geo:label "Steady-only transient attempt" .
"""

    def test_valid_event_conforms(self):
        conforms, violations = _validate_ttl(self.VALID_TTL)
        self.assertTrue(conforms, f"Expected conformance; violations: {violations}")

    def test_invalid_label_fires(self):
        conforms, violations = _validate_ttl(self.INVALID_LABEL_TTL)
        self.assertFalse(conforms, "Expected violation for label=99")

    def test_transient_forbidden_for_steady_fires(self):
        conforms, violations = _validate_ttl(self.INVALID_TRANSIENT_TTL)
        self.assertFalse(conforms, "Expected violation for label=103 (class 3 is steady-only)")


@unittest.skipUnless(PYSHACL_AVAILABLE, "pyshacl not installed")
class TestSensor3WShape(unittest.TestCase):
    """geo:Sensor3WShape — threewUnit required, threewQuantityKind in enum."""

    VALID_TTL = PREFIXES + """
geo:sensor_p_pdg a geo:Sensor3W ;
    geo:threewUnit "Pa" ;
    geo:threewQuantityKind "Pressure" ;
    geo:label "P-PDG" .
"""

    MISSING_UNIT_TTL = PREFIXES + """
geo:sensor_bad a geo:Sensor3W ;
    geo:threewQuantityKind "Pressure" ;
    geo:label "Bad Sensor" .
"""

    INVALID_KIND_TTL = PREFIXES + """
geo:sensor_bad2 a geo:Sensor3W ;
    geo:threewUnit "Pa" ;
    geo:threewQuantityKind "Energy" ;
    geo:label "Bad Kind Sensor" .
"""

    def test_valid_sensor_conforms(self):
        conforms, violations = _validate_ttl(self.VALID_TTL)
        self.assertTrue(conforms, f"Expected conformance; violations: {violations}")

    def test_missing_unit_fires(self):
        conforms, violations = _validate_ttl(self.MISSING_UNIT_TTL)
        self.assertFalse(conforms, "Expected violation for missing threewUnit")

    def test_invalid_kind_fires(self):
        conforms, violations = _validate_ttl(self.INVALID_KIND_TTL)
        self.assertFalse(conforms, "Expected violation for threewQuantityKind='Energy'")


@unittest.skipUnless(PYSHACL_AVAILABLE, "pyshacl not installed")
class TestValveStateShape(unittest.TestCase):
    """geo:ValveStateShape — value must be 0, 0.5, or 1."""

    VALID_TTL = PREFIXES + """
geo:obs_dhsv_closed a geo:ValveStateObservation ;
    geo:value 0 ;
    geo:label "DHSV closed" .
"""

    VALID_PARTIAL_TTL = PREFIXES + """
geo:obs_dhsv_partial a geo:ValveStateObservation ;
    geo:value 0.5 ;
    geo:label "DHSV partial" .
"""

    INVALID_VALUE_TTL = PREFIXES + """
geo:obs_dhsv_bad a geo:ValveStateObservation ;
    geo:value 0.3 ;
    geo:label "Bad valve state" .
"""

    def test_valid_value_0_conforms(self):
        conforms, violations = _validate_ttl(self.VALID_TTL)
        self.assertTrue(conforms, f"Expected conformance for value=0; violations: {violations}")

    def test_valid_value_0_5_conforms(self):
        conforms, violations = _validate_ttl(self.VALID_PARTIAL_TTL)
        self.assertTrue(conforms, f"Expected conformance for value=0.5; violations: {violations}")

    def test_invalid_value_fires(self):
        conforms, violations = _validate_ttl(self.INVALID_VALUE_TTL)
        self.assertFalse(conforms, "Expected violation for value=0.3")


if __name__ == "__main__":
    unittest.main()
