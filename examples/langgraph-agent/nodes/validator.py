"""SemanticValidator node — deterministic checks against data/taxonomies.json.

This node never calls an LLM. All rules are implemented as pure functions
over the loaded taxonomy data and the question text.

Rules enforced
--------------
1. SPE_PRMS_INVALID_CATEGORY
   "Reserva 4P" is not a valid SPE-PRMS category. Only 1P, 2P, 3P exist
   under Reservas; C1C/C2C/C3C exist under Recursos Contingentes.

2. RESERVA_AMBIENTAL_CONFUSION
   "Reserva" in the O&G context (SPE-PRMS) must not be confused with
   "Reserva Ambiental" (REBIO, RPPN, APA) which is an environmental
   protection area. The validator flags this confusion.

3. REGIME_CONTRATUAL_INVALID
   The contract regime must be one of: Concessão, Partilha de Produção,
   Cessão Onerosa. Any other value is invalid.

4. TIPO_POCO_ANP_INVALID
   The ANP well-type prefix must be one of the canonical values from the
   tipo_poco taxonomy (exploratorio/1-, avaliacao/2-, desenvolvimento/3-
   or 7-, especial/4- or 6-).
"""

from __future__ import annotations

import re
from typing import Any

from data_loader import load_taxonomies
from state import AgentState, ValidationResult, Violation

# ---------------------------------------------------------------------------
# Canonical value sets (derived from taxonomies.json at import time)
# ---------------------------------------------------------------------------

_VALID_SPE_PRMS_RESERVES = {"1P", "2P", "3P"}
_VALID_SPE_PRMS_CONTINGENT = {"C1C", "C2C", "C3C"}
_VALID_SPE_PRMS_ALL = _VALID_SPE_PRMS_RESERVES | _VALID_SPE_PRMS_CONTINGENT

_VALID_REGIMES = {
    "concessão",
    "concessao",
    "partilha de produção",
    "partilha de producao",
    "partilha",
    "cessão onerosa",
    "cessao onerosa",
}

# Environmental reserve keywords that indicate confusion
_AMBIENTAL_SIGNALS = [
    "rebio",
    "rppn",
    "apa",
    "reserva ambiental",
    "reserva biologica",
    "reserva biológica",
    "reserva particular",
    "area de protecao",
    "área de proteção",
]

# ANP well-type canonical prefixes
_ANP_WELL_PREFIXES = {"1", "2", "3", "4", "6", "7"}


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------


def _check_spe_prms_invalid_category(text: str) -> list[Violation]:
    """Flag any mention of 4P (or other non-canonical SPE-PRMS labels)."""
    violations: list[Violation] = []

    # Pattern: "reserva 4P" or just "4P" as a standalone term
    if re.search(r"\b4\s*[Pp]\b", text):
        violations.append(
            {
                "rule": "SPE_PRMS_INVALID_CATEGORY",
                "evidence": "Menção a '4P' no texto.",
                "suggested_fix": (
                    "A classificação SPE-PRMS não reconhece '4P'. "
                    "Categorias válidas para Reservas: 1P (Provadas), 2P (Prováveis), 3P (Possíveis). "
                    "Para Recursos Contingentes: C1C, C2C, C3C."
                ),
            }
        )

    # Generic pattern for other bogus reserve codes like 5P, 6P
    for match in re.finditer(r"\b([5-9][Pp]|[1-9][0-9]+[Pp])\b", text):
        label = match.group(1).upper()
        violations.append(
            {
                "rule": "SPE_PRMS_INVALID_CATEGORY",
                "evidence": f"Menção a '{label}' no texto.",
                "suggested_fix": (
                    f"'{label}' não é uma categoria SPE-PRMS válida. "
                    "Categorias válidas para Reservas: 1P, 2P, 3P."
                ),
            }
        )

    return violations


def _check_reserva_ambiental_confusion(text: str) -> list[Violation]:
    """Flag potential confusion between Reserva (SPE-PRMS) and Reserva Ambiental."""
    violations: list[Violation] = []
    text_lower = text.lower()

    has_reserva = "reserva" in text_lower
    has_oil_context = any(
        kw in text_lower
        for kw in [
            "campo", "bloco", "petroleo", "petróleo", "gas", "gás",
            "boe", "mboe", "bboe", "spe", "prms",
            "oleo", "óleo", "barris", "hidrocarboneto", "producao", "produção",
            "1p", "2p", "3p", "c1c", "c2c", "c3c", "provadas", "provaveis",
            "contingentes", "mmb", "bcf",
        ]
    )
    has_ambiental_signal = any(sig in text_lower for sig in _AMBIENTAL_SIGNALS)

    if has_reserva and has_ambiental_signal and has_oil_context:
        violations.append(
            {
                "rule": "RESERVA_AMBIENTAL_CONFUSION",
                "evidence": (
                    "O texto menciona 'reserva' em contexto de petróleo/gás "
                    "mas também contém termos de reserva ambiental (REBIO, RPPN, APA, etc.)."
                ),
                "suggested_fix": (
                    "Desambiguar: 'Reserva' no contexto SPE-PRMS refere-se a volumes de hidrocarbonetos "
                    "tecnicamente recuperáveis e comercialmente viáveis (1P/2P/3P). "
                    "'Reserva Ambiental' (REBIO/RPPN/APA) é uma área de proteção ambiental "
                    "regulada pelo SNUC (Lei 9.985/2000) e não tem relação com volumes petrolíferos."
                ),
            }
        )

    return violations


def _check_regime_contratual(text: str) -> list[Violation]:
    """Flag regime contratual mentions that are not canonical."""
    violations: list[Violation] = []
    text_lower = text.lower()

    # Only evaluate if the text explicitly discusses contract regime
    regime_keywords = [
        "regime contratual",
        "regime de",
        "modalidade contratual",
        "regime exploratório",
        "regime explorat",
        "contrato de",
    ]
    if not any(kw in text_lower for kw in regime_keywords):
        return violations

    # Extract candidate regime name.
    # Patterns we handle:
    #   "regime contratual e/é Concessão"
    #   "regime contratual de Partilha"
    #   "regime contratual: Cessão Onerosa"
    # We anchor tightly after the copula / preposition so we don't slurp up
    # noun phrases that precede the regime name (e.g. "do bloco e").
    match = re.search(
        r"regime\s+contratual\s+(?:(?:é|e)\s+(?:o\s+)?|de\s+|:\s*)"
        r"([A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+(?:\s+[A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+){0,3}?)"
        r"(?:\s*[,\.\?!\n]|$)",
        text,
        re.IGNORECASE,
    )
    if match:
        candidate = match.group(1).strip().lower()
        if candidate and candidate not in _VALID_REGIMES:
            violations.append(
                {
                    "rule": "REGIME_CONTRATUAL_INVALID",
                    "evidence": f"Regime contratual mencionado: '{candidate}'.",
                    "suggested_fix": (
                        "Regimes contratuais válidos no Brasil: "
                        "Concessão (Lei 9.478/1997), "
                        "Partilha de Produção (Lei 12.351/2010), "
                        "Cessão Onerosa (Lei 12.276/2010)."
                    ),
                }
            )

    return violations


def _check_tipo_poco_anp(text: str) -> list[Violation]:
    """Flag ANP well codes that don't match the canonical prefix convention."""
    violations: list[Violation] = []

    # ANP codes follow the pattern: N-XXX-NNN-UF (e.g., 1-RJS-702-RJ)
    # The first digit is the type prefix
    for match in re.finditer(r"\b([0-9])-[A-Z]{2,4}-[0-9]+-[A-Z]{2}\b", text):
        full_code = match.group(0)
        prefix = match.group(1)
        if prefix not in _ANP_WELL_PREFIXES:
            violations.append(
                {
                    "rule": "TIPO_POCO_ANP_INVALID",
                    "evidence": f"Código de poço ANP '{full_code}' com prefixo '{prefix}-' desconhecido.",
                    "suggested_fix": (
                        "Prefixos ANP válidos: "
                        "1- (Exploratório), 2- (Avaliação), "
                        "3- ou 7- (Desenvolvimento), 4- ou 6- (Especial)."
                    ),
                }
            )

    return violations


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------


def validator_node(state: AgentState) -> AgentState:
    """Run all deterministic validation rules against the question and draft.

    Writes `validation` (ValidationResult) into state.
    """
    # Check both the original question and the current draft (if present)
    text_to_check = state.get("draft", "") + " " + state.get("question", "")

    violations: list[Violation] = []
    violations.extend(_check_spe_prms_invalid_category(text_to_check))
    violations.extend(_check_reserva_ambiental_confusion(text_to_check))
    violations.extend(_check_regime_contratual(text_to_check))
    violations.extend(_check_tipo_poco_anp(text_to_check))

    validation: ValidationResult = {
        "valid": len(violations) == 0,
        "violations": violations,
    }

    return {**state, "validation": validation}
