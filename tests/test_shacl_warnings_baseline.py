"""SHACL warnings baseline — drift detection for the live ontology graph.

Falhar este teste significa que `data/geobrain.ttl` regrediu (mais warnings
SHACL do que o baseline). Atualize as constantes BASELINE_* APENAS após
revisão do curador, garantindo que o aumento foi consciente e justificado.

Run:
    python3 -m pytest tests/test_shacl_warnings_baseline.py -v
    python3 -m pytest tests/test_shacl_warnings_baseline.py -v -s   # mostra prints

A validação roda contra:
    - data/geobrain.ttl (live graph, source-of-truth)
    - data/ontology-layers-shapes.ttl (F6 SHACL shapes do modelo de 6 camadas)

Inspirado em tests/test_ontology_layers_shacl.py — mas o foco aqui é
quantitativo (contagem de warnings) e não qualitativo (firing por shape).
"""

from __future__ import annotations

import unittest
from collections import Counter
from pathlib import Path

import pyshacl
from rdflib import Graph, Namespace
from rdflib.namespace import RDF

ROOT = Path(__file__).resolve().parents[1]
DATA_TTL = ROOT / "data" / "geobrain.ttl"
SHAPES = ROOT / "data" / "ontology-layers-shapes.ttl"

SH = Namespace("http://www.w3.org/ns/shacl#")

# ─────────────────────────── Baseline constants ───────────────────────────
#
# Total warnings (current 191; small buffer for noise no curado).
BASELINE_WARNINGS = 200

# Per-shape ceiling. Fonte: snapshot da live graph em 2026-05-04.
# Ajuste estes valores APÓS revisão do curador quando houver crescimento
# consciente da base de dados.
BASELINE_PER_SHAPE = {
    "FeatureObservationAnchoredShape": 90,           # current 78
    "InterpretationProcessHasInputOutputShape": 50,  # current 37
    "WellOperationHasActorOrLocationShape": 35,      # current 26
    "ArtifactPrimaryFromOperationShape": 25,         # current 19
    "DatasetConceptReferencesOriginShape": 25,       # current 16
    "EngineeringArtifactAppliesToShape": 15,         # current 6
    "DomainAnchorClassifiesShape": 5,                # current 1
}


def _local_name(uri: str) -> str:
    """Extract the local name (last segment after `#` or `/`) of a SHACL URI."""
    if not uri:
        return ""
    if "#" in uri:
        return uri.rsplit("#", 1)[-1]
    return uri.rsplit("/", 1)[-1]


def _validate_live() -> tuple[list[dict], list[dict]]:
    """Run pyshacl on the live graph and split findings into warnings + violations.

    Returns:
        (warnings, violations) — each is a list of dicts with keys
        `severity`, `message`, `focus`, `source` (str URIs).
    """
    shapes_g = Graph().parse(str(SHAPES), format="turtle")
    data_g = Graph().parse(str(DATA_TTL), format="turtle")
    _conforms, results_g, _ = pyshacl.validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        inference=None,
        abort_on_first=False,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        js=False,
    )
    warnings: list[dict] = []
    violations: list[dict] = []
    for v in results_g.subjects(RDF.type, SH.ValidationResult):
        sev = next(iter(results_g.objects(v, SH.resultSeverity)), None)
        msg = next(iter(results_g.objects(v, SH.resultMessage)), "")
        focus = next(iter(results_g.objects(v, SH.focusNode)), "")
        source = next(iter(results_g.objects(v, SH.sourceShape)), "")
        rec = {
            "severity": str(sev) if sev else "",
            "message": str(msg),
            "focus": str(focus),
            "source": str(source),
        }
        if rec["severity"].endswith("#Warning"):
            warnings.append(rec)
        elif rec["severity"].endswith("#Violation"):
            violations.append(rec)
    return warnings, violations


class TestShaclWarningsBaseline(unittest.TestCase):
    """Snapshot-style drift tests on the live graph (geobrain.ttl).

    setUpClass roda pyshacl uma única vez (validação completa custa
    ~60s), populando atributos de classe usados pelos vários testes.
    """

    warnings: list[dict] = []
    violations: list[dict] = []

    @classmethod
    def setUpClass(cls) -> None:
        cls.warnings, cls.violations = _validate_live()

    # ── Test 1 ────────────────────────────────────────────────────────────
    def test_warning_count_within_baseline(self) -> None:
        """Total de warnings <= BASELINE_WARNINGS."""
        n = len(self.warnings)
        self.assertLessEqual(
            n,
            BASELINE_WARNINGS,
            f"SHACL warnings regressed: got {n}, baseline is {BASELINE_WARNINGS}. "
            f"Investigate before bumping the constant. "
            f"Top sources: {Counter(_local_name(w['source']) for w in self.warnings).most_common(5)}",
        )

    # ── Test 2 ────────────────────────────────────────────────────────────
    def test_no_violations_on_live_graph(self) -> None:
        """sh:Violation severity == 0 (regras duras devem sempre passar)."""
        n = len(self.violations)
        self.assertEqual(
            n,
            0,
            f"Live graph should have 0 hard Violations. Got {n}. "
            f"First few: "
            + "; ".join(
                f"[{_local_name(v['source'])}] {v['message'][:90]}"
                for v in self.violations[:5]
            ),
        )

    # ── Test 3 ────────────────────────────────────────────────────────────
    def test_warnings_distribution(self) -> None:
        """Warnings agrupados por sourceShape — cada shape abaixo do teto."""
        per_shape = Counter(_local_name(w["source"]) for w in self.warnings)
        offenders: list[str] = []
        for shape, ceiling in BASELINE_PER_SHAPE.items():
            actual = per_shape.get(shape, 0)
            if actual > ceiling:
                offenders.append(f"{shape}: {actual} > {ceiling}")
        self.assertEqual(
            len(offenders),
            0,
            "Per-shape warning ceiling exceeded — investigate before bumping:\n  "
            + "\n  ".join(offenders),
        )

    # ── Test 4 ────────────────────────────────────────────────────────────
    def test_baseline_decreases_over_time(self) -> None:
        """Informacional — imprime a contagem atual para visibilidade.

        NÃO falha. Use `pytest -s` para visualizar o output. Serve como
        sinal contínuo para o curador acompanhar o progresso de F4/F7
        (eliminação progressiva dos warnings).
        """
        per_shape = Counter(_local_name(w["source"]) for w in self.warnings)
        print(f"\n[baseline] total SHACL warnings on live graph: {len(self.warnings)}")
        print(f"[baseline] hard violations: {len(self.violations)}")
        print("[baseline] per-shape breakdown:")
        for shape, n in per_shape.most_common():
            ceiling = BASELINE_PER_SHAPE.get(shape, "—")
            print(f"  {n:4d} / {ceiling}  {shape}")
        # Sem assert — apenas visibilidade.


if __name__ == "__main__":
    unittest.main()
