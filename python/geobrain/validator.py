"""validator.py — Python port of scripts/semantic-validator.js.

Rule IDs and messages are kept identical to the JS implementation so that the
two validators produce the same output for the same inputs.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from .data import load_json


# ---------------------------------------------------------------------------
# Public return types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Violation:
    """A single validation violation or warning."""

    rule: str
    severity: str  # "error" | "warning"
    evidence: str
    suggested_fix: str
    source_layer: str


@dataclass
class Report:
    """Result of a validation run."""

    valid: bool
    violations: list[Violation] = field(default_factory=list)
    warnings: list[Violation] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid


# ---------------------------------------------------------------------------
# Canonical value sets (mirrors semantic-validator.js)
# ---------------------------------------------------------------------------

_VALID_SPE_PRMS_RESERVES: frozenset[str] = frozenset({"1P", "2P", "3P"})
_VALID_SPE_PRMS_CONTINGENT: frozenset[str] = frozenset({"C1C", "C2C", "C3C"})

_VALID_REGIMES: frozenset[str] = frozenset({
    "concessão",
    "concessao",
    "partilha de produção",
    "partilha de producao",
    "partilha",
    "cessão onerosa",
    "cessao onerosa",
})

_AMBIENTAL_SIGNALS: list[str] = [
    "rebio", "rppn", "apa ", " apa", "reserva ambiental",
    "reserva biologica", "reserva biológica", "reserva particular",
    "area de protecao", "área de proteção",
    "unidade de conservacao", "unidade de conservação", "snuc",
]

_OIL_GAS_KEYWORDS: list[str] = [
    "campo", "bloco", "petroleo", "petróleo", "gas", "gás",
    "boe", "mboe", "bboe", "spe", "prms", "oleo", "óleo",
    "barris", "hidrocarboneto", "producao", "produção", "1p", "2p", "3p",
    "c1c", "c2c", "c3c", "provadas", "provaveis", "contingentes",
    "mmb", "bcf", "reservatorio", "reservatório",
]

_ANP_WELL_PREFIXES: frozenset[str] = frozenset({"1", "2", "3", "4", "6", "7"})

# Regex mirrors JS: /^opendes:osdu:[a-z-]+--[A-Z][a-zA-Z]+:\d+\.\d+\.\d+$/
_OSDU_KIND_REGEX = re.compile(
    r"^opendes:osdu:[a-z-]+--[A-Z][a-zA-Z]+:\d+\.\d+\.\d+$"
)

_KNOWN_AMBIGUOUS: frozenset[str] = frozenset({
    "PAD", "UTS", "GAS", "GÁS", "APA", "BOP", "API", "LWD", "MWD"
})

_DISAMBIGUATION_CONTEXTS: list[str] = [
    "plano de avaliacao", "plano de avaliação", "drilling pad", "pad explorat",
    "unidades de trabalho", "unidade territorial", "api gravity", "api grau",
    "bloqueador de poc", "blowout preventer",
]

_BOUNDARY_RE = re.compile(
    r"\s+(?:para|com|nos|nas|no|na|sobre|entre|até|pelos?|pelas?|num|numa|pelo)\b",
    re.IGNORECASE,
)

_LIT_KEYWORDS: list[str] = [
    "litologia", "litológic", "litologic", "rocha",
    "lithology", "tipo de rocha", "fácies",
]

_JANELA_KEYWORDS: list[str] = [
    "janela de geração", "janela de geracao",
    "janela de maturação", "maturidade termica", "maturidade térmica",
    "vitrinita", "querogênio", "querogênio",
]

_REGIME_KEYWORDS: list[str] = [
    "regime contratual", "regime de", "modalidade contratual",
    "regime explorat", "contrato de",
]


# ---------------------------------------------------------------------------
# Data loading (lazy, loaded once per Validator instance)
# ---------------------------------------------------------------------------

class _DataStore:
    """Cached data loaded from bundled JSON files."""

    def __init__(self) -> None:
        self._full: dict[str, Any] | None = None
        self._taxonomies: dict[str, Any] | None = None
        self._entity_graph: dict[str, Any] | None = None

    def _load_all(self) -> None:
        if self._full is not None:
            return
        try:
            self._full = load_json("full.json")
        except FileNotFoundError:
            self._full = {}
        try:
            self._taxonomies = load_json("taxonomies.json")
        except FileNotFoundError:
            self._taxonomies = {}
        try:
            self._entity_graph = load_json("entity-graph.json")
        except FileNotFoundError:
            self._entity_graph = {}

    @property
    def full(self) -> dict[str, Any]:
        self._load_all()
        return self._full or {}  # type: ignore[return-value]

    @property
    def taxonomies(self) -> dict[str, Any]:
        self._load_all()
        return self._taxonomies or {}  # type: ignore[return-value]

    @property
    def entity_graph(self) -> dict[str, Any]:
        self._load_all()
        return self._entity_graph or {}  # type: ignore[return-value]


# Singleton store shared across Validator instances in the same process
_store = _DataStore()


def _build_lithology_set() -> frozenset[str]:
    taxonomies = _store.taxonomies
    tipo = taxonomies.get("taxonomies", taxonomies).get("tipo_litologia")
    if not tipo:
        return frozenset({
            "arenito", "conglomerado", "folhelho", "argilito",
            "calcario", "dolomito", "marga", "siliciclastico", "carbonatico",
        })
    values = tipo.get("values", {})
    result: set[str] = set()
    for key, cat in values.items():
        result.add(key)
        for child in cat.get("children", []):
            result.add(child)
    return frozenset(result)


def _build_kerogen_set() -> frozenset[str]:
    taxonomies = _store.taxonomies
    tipo = taxonomies.get("taxonomies", taxonomies).get("tipo_querogeno")
    if not tipo:
        return frozenset({
            "tipo_i", "tipo_ii", "tipo_iis", "tipo_iii", "tipo_iv",
            "tipo i", "tipo ii", "tipo iii", "tipo iv",
        })
    values = tipo.get("values", {})
    result: set[str] = set()
    for key in values:
        result.add(key.lower())
        result.add(key.lower().replace("_", " "))
    return frozenset(result)


def _build_window_set() -> frozenset[str]:
    taxonomies = _store.taxonomies
    tipo = taxonomies.get("taxonomies", taxonomies).get("janela_geracao")
    if not tipo:
        return frozenset({
            "imaturo", "janela_oleo", "janela de óleo",
            "gas_umido", "gas_seco", "sobrematuro",
        })
    values = tipo.get("values", [])
    result: set[str] = set()
    if isinstance(values, list):
        for v in values:
            result.add(v["id"].lower())
            result.add(v["label"].lower())
    elif isinstance(values, dict):
        for k, v in values.items():
            result.add(k.lower())
            if isinstance(v, dict):
                result.add(v.get("label", "").lower())
    return frozenset(result)


def _build_entity_layer_map() -> dict[str, frozenset[str]]:
    eg = _store.entity_graph
    result: dict[str, frozenset[str]] = {}
    for node in eg.get("nodes", []):
        nid = node.get("id", "")
        coverage = node.get("geocoverage", [])
        if nid and isinstance(coverage, list):
            result[nid] = frozenset(coverage)
    return result


def _build_acronym_map() -> dict[str, list[dict[str, Any]]]:
    full = _store.full
    acronyms = full.get("acronyms", [])
    result: dict[str, list[dict[str, Any]]] = {}
    for a in acronyms:
        sigla = a.get("sigla", "").upper()
        if sigla not in result:
            result[sigla] = []
        result[sigla].append({
            "expansion_pt": a.get("expansion_pt", ""),
            "expansion_en": a.get("expansion_en", ""),
            "category": a.get("category", ""),
        })
    return result


# ---------------------------------------------------------------------------
# Rule implementations — mirror JS function names
# ---------------------------------------------------------------------------

def _check_spe_prms_invalid_category(text: str) -> list[Violation]:
    violations: list[Violation] = []

    if re.search(r"\b4\s*[Pp]\b", text):
        violations.append(Violation(
            rule="SPE_PRMS_INVALID_CATEGORY",
            severity="error",
            evidence="Menção a '4P' no texto.",
            suggested_fix=(
                "A classificação SPE-PRMS não reconhece '4P'. "
                "Categorias válidas para Reservas: 1P (Provadas), 2P (Prováveis), 3P (Possíveis). "
                "Para Recursos Contingentes: C1C, C2C, C3C."
            ),
            source_layer="taxonomies/categoria_recurso_spe_prms",
        ))

    for m in re.finditer(r"\b([5-9][Pp]|[1-9][0-9]+[Pp])\b", text):
        label = m.group(1).upper()
        violations.append(Violation(
            rule="SPE_PRMS_INVALID_CATEGORY",
            severity="error",
            evidence=f"Menção a '{label}' no texto.",
            suggested_fix=(
                f"'{label}' não é uma categoria SPE-PRMS válida. "
                "Categorias válidas para Reservas: 1P, 2P, 3P."
            ),
            source_layer="taxonomies/categoria_recurso_spe_prms",
        ))

    return violations


def _check_reserva_ambiguity(text: str) -> list[Violation]:
    lower = text.lower()
    has_reserva = "reserva" in lower
    has_oil_context = any(kw in lower for kw in _OIL_GAS_KEYWORDS)
    has_ambiental = any(sig in lower for sig in _AMBIENTAL_SIGNALS)

    if has_reserva and has_ambiental and has_oil_context:
        return [Violation(
            rule="RESERVA_AMBIGUITY",
            severity="warning",
            evidence=(
                "O texto menciona 'reserva' em contexto de petróleo/gás "
                "mas também contém termos de reserva ambiental (REBIO, RPPN, APA, etc.)."
            ),
            suggested_fix=(
                "Desambiguar: 'Reserva' no contexto SPE-PRMS refere-se a volumes de hidrocarbonetos "
                "tecnicamente recuperáveis e comercialmente viáveis (1P/2P/3P). "
                "'Reserva Ambiental' (REBIO/RPPN/APA) é uma área de proteção ambiental "
                "regulada pelo SNUC (Lei 9.985/2000) e não tem relação com volumes petrolíferos."
            ),
            source_layer="taxonomies/categoria_recurso_spe_prms",
        )]
    return []


def _check_regime_contratual(text: str) -> list[Violation]:
    lower = text.lower()
    if not any(kw in lower for kw in _REGIME_KEYWORDS):
        return []

    raw_match = re.search(
        r"regime\s+(?:contratual\s+)?(?:(?:é|e|de|em)\s+(?:o\s+)?|:\s*)"
        r"([A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+(?:\s+[A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+){0,3})",
        text,
        re.IGNORECASE,
    )

    if not raw_match:
        return []

    trimmed = _BOUNDARY_RE.sub("", raw_match.group(1)).strip()
    if not trimmed:
        return []

    candidate = trimmed.lower()
    if candidate and candidate not in _VALID_REGIMES:
        return [Violation(
            rule="REGIME_CONTRATUAL_INVALID",
            severity="error",
            evidence=f"Regime contratual mencionado: '{candidate}'.",
            suggested_fix=(
                "Regimes contratuais válidos no Brasil: "
                "Concessão (Lei 9.478/1997), "
                "Partilha de Produção (Lei 12.351/2010), "
                "Cessão Onerosa (Lei 12.276/2010)."
            ),
            source_layer="entity-graph/regime-contratual",
        )]
    return []


def _check_tipo_poco_invalid(text: str) -> list[Violation]:
    violations: list[Violation] = []
    for m in re.finditer(r"\b([0-9])-[A-Z]{2,4}-[0-9]+-[A-Z]{2,4}\b", text):
        full_code = m.group(0)
        prefix = m.group(1)
        if prefix not in _ANP_WELL_PREFIXES:
            violations.append(Violation(
                rule="TIPO_POCO_INVALID",
                severity="error",
                evidence=f"Código de poço ANP '{full_code}' com prefixo '{prefix}-' desconhecido.",
                suggested_fix=(
                    "Prefixos ANP válidos: "
                    "1- (Exploratório), 2- (Avaliação), "
                    "3- ou 7- (Desenvolvimento), 4- ou 6- (Especial)."
                ),
                source_layer="taxonomies/tipo_poco",
            ))
    return violations


def _check_litologia_invalid(text: str, valid_lithologies: frozenset[str]) -> list[Violation]:
    lower = text.lower()
    if not any(kw in lower for kw in _LIT_KEYWORDS):
        return []

    violations: list[Violation] = []
    for m in re.finditer(
        r"(?:litologia|tipo de rocha|lithology)[:\s]+([a-záéíóúâêîôûàãõç]+)",
        lower,
    ):
        candidate = m.group(1).strip()
        candidate_underscored = candidate.replace(" ", "_")
        if candidate not in valid_lithologies and candidate_underscored not in valid_lithologies:
            violations.append(Violation(
                rule="LITOLOGIA_INVALID",
                severity="warning",
                evidence=f"Litologia '{candidate}' não reconhecida na taxonomia canônica.",
                suggested_fix=(
                    f"Litologias válidas (taxonomia CGI/GeoSciML): {', '.join(sorted(valid_lithologies))}."
                ),
                source_layer="taxonomies/tipo_litologia",
            ))
    return violations


def _check_janela_geracao_invalid(text: str, valid_windows: frozenset[str]) -> list[Violation]:
    lower = text.lower()
    if not any(kw in lower for kw in _JANELA_KEYWORDS):
        return []

    violations: list[Violation] = []
    for m in re.finditer(
        r"janela\s+de\s+([a-záéíóúâêîôûàãõç]+)(?:\s+([a-záéíóúâêîôûàãõç]+))?",
        lower,
    ):
        word1 = m.group(1)
        word2 = m.group(2)
        candidate = word1
        if word2:
            two_words = f"{word1} {word2}"
            if two_words in valid_windows or f"janela de {two_words}" in valid_windows:
                candidate = two_words
        window_label = f"janela de {candidate}"
        if candidate not in valid_windows and window_label not in valid_windows:
            violations.append(Violation(
                rule="JANELA_GERACAO_INVALID",
                severity="warning",
                evidence=f"Janela de geração '{candidate}' não reconhecida.",
                suggested_fix=(
                    f"Janelas válidas: {', '.join(sorted(valid_windows))}. "
                    "Baseadas na reflectância da vitrinita (Ro%)."
                ),
                source_layer="taxonomies/janela_geracao",
            ))
    return violations


def _check_acronym_ambiguous(
    text: str, acronym_map: dict[str, list[dict[str, Any]]]
) -> list[Violation]:
    upper = text.upper()
    lower = text.lower()
    seen: set[str] = set()
    violations: list[Violation] = []

    for m in re.finditer(r"\b([A-Z]{2,6})\b", upper):
        sigla = m.group(1)
        if sigla in seen:
            continue
        seen.add(sigla)
        if sigla not in _KNOWN_AMBIGUOUS:
            continue

        entries = acronym_map.get(sigla, [])
        is_ambiguous = len(entries) > 1
        is_known_ambiguous = sigla in _KNOWN_AMBIGUOUS

        if is_ambiguous or is_known_ambiguous:
            has_context = any(ctx in lower for ctx in _DISAMBIGUATION_CONTEXTS)
            if not has_context:
                meanings = " / ".join(
                    filter(None, (
                        e.get("expansion_pt") or e.get("expansion_en")
                        for e in entries
                    ))
                ) or "(múltiplos sentidos)"
                violations.append(Violation(
                    rule="ACRONYM_AMBIGUOUS",
                    severity="warning",
                    evidence=f"Sigla '{sigla}' tem múltiplos sentidos no domínio O&G: {meanings}.",
                    suggested_fix=(
                        f"Incluir contexto de desambiguação ao usar '{sigla}'. "
                        "Exemplo: especificar se é o sentido regulatório (ANP), operacional ou geomecânico."
                    ),
                    source_layer="acronyms",
                ))
    return violations


def _check_osdu_kind_format(text: str) -> list[Violation]:
    violations: list[Violation] = []
    for m in re.finditer(r"\bopendes:[^\s,;'\"]+|osdu:[a-z-]+--[A-Za-z][^\s,;'\"]+", text):
        candidate = m.group(0)
        if not _OSDU_KIND_REGEX.match(candidate):
            violations.append(Violation(
                rule="OSDU_KIND_FORMAT",
                severity="error",
                evidence=f"OSDU kind '{candidate}' não segue o padrão canônico.",
                suggested_fix=(
                    "Formato correto: 'opendes:osdu:<domain>--<Type>:<major>.<minor>.<patch>'. "
                    "Exemplo: 'opendes:osdu:master-data--Well:1.0.0'."
                ),
                source_layer="entity-graph/osdu_kind",
            ))
    return violations


def _check_layer_coverage_mismatch(
    claim: dict[str, Any],
    entity_layer_map: dict[str, frozenset[str]],
) -> list[Violation]:
    value = claim.get("value", "")
    context = claim.get("context")
    if not value or not context:
        return []

    entity_id = context.get("entity_id", "")
    asserted_layer = context.get("layer")

    if not entity_id or not asserted_layer:
        return []

    entity_id_norm = entity_id.lower().replace(" ", "-")
    coverage = entity_layer_map.get(entity_id_norm)
    if coverage is None:
        return []

    if asserted_layer not in coverage:
        return [Violation(
            rule="LAYER_COVERAGE_MISMATCH",
            severity="warning",
            evidence=(
                f"Entidade '{entity_id_norm}' não tem cobertura na camada '{asserted_layer}'. "
                f"Camadas cobertas: {', '.join(sorted(coverage))}."
            ),
            suggested_fix=(
                f"Verificar a cobertura da entidade '{entity_id_norm}' no entity-graph.json. "
                f"A camada '{asserted_layer}' não está no campo geocoverage desta entidade."
            ),
            source_layer="entity-graph/geocoverage",
        )]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class Validator:
    """Semantic validator for Geolytics domain claims.

    Mirrors the rule IDs and messages of ``scripts/semantic-validator.js`` so
    both implementations report identical violations for identical inputs.

    Usage::

        v = Validator()
        report = v.validate("Reserva 4P do Campo de Búzios")
        # Report(valid=False, violations=[Violation(rule='SPE_PRMS_INVALID_CATEGORY', ...)])

        # Structured claim for LAYER_COVERAGE_MISMATCH:
        report = v.validate({"value": "poco", "context": {"entity_id": "poco", "layer": "layer9"}})
    """

    @cached_property
    def _valid_lithologies(self) -> frozenset[str]:
        return _build_lithology_set()

    @cached_property
    def _valid_windows(self) -> frozenset[str]:
        return _build_window_set()

    @cached_property
    def _entity_layer_map(self) -> dict[str, frozenset[str]]:
        return _build_entity_layer_map()

    @cached_property
    def _acronym_map(self) -> dict[str, list[dict[str, Any]]]:
        return _build_acronym_map()

    def validate(self, claim: str | dict[str, Any]) -> Report:
        """Validate a claim.

        Args:
            claim: Either a free-text string, or a structured dict with keys
                ``value`` (str) and optionally ``context`` (dict with
                ``entity_id`` and ``layer`` for LAYER_COVERAGE_MISMATCH).

        Returns:
            A :class:`Report` instance with ``valid``, ``violations``
            (severity=error), and ``warnings`` (severity=warning).
        """
        if isinstance(claim, str):
            text = claim
            structured: dict[str, Any] | None = None
        elif isinstance(claim, dict):
            text = claim.get("value", "")
            structured = claim
        else:
            return Report(
                valid=False,
                violations=[Violation(
                    rule="INVALID_INPUT",
                    severity="error",
                    evidence="claim must be a string or object with .value",
                    suggested_fix="Pass a string or { type, value, context }.",
                    source_layer="validator",
                )],
            )

        all_violations = (
            _check_spe_prms_invalid_category(text)
            + _check_reserva_ambiguity(text)
            + _check_regime_contratual(text)
            + _check_tipo_poco_invalid(text)
            + _check_litologia_invalid(text, self._valid_lithologies)
            + _check_janela_geracao_invalid(text, self._valid_windows)
            + _check_acronym_ambiguous(text, self._acronym_map)
            + _check_osdu_kind_format(text)
            + (
                _check_layer_coverage_mismatch(structured, self._entity_layer_map)
                if structured is not None
                else []
            )
        )

        violations = [v for v in all_violations if v.severity == "error"]
        warnings = [v for v in all_violations if v.severity == "warning"]

        return Report(valid=len(violations) == 0, violations=violations, warnings=warnings)
