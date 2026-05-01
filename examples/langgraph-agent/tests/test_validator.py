"""Tests for the SemanticValidator node.

All tests are deterministic: no LLM or network calls are made.
Run with: pytest examples/langgraph-agent/tests/test_validator.py -v
"""

from __future__ import annotations

import os
import sys

# Make the agent package importable regardless of cwd
_AGENT_DIR = os.path.join(os.path.dirname(__file__), "..")
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

import pytest

from nodes.validator import (
    _check_spe_prms_invalid_category,
    _check_reserva_ambiental_confusion,
    _check_regime_contratual,
    _check_tipo_poco_anp,
    validator_node,
)
from state import AgentState


# ---------------------------------------------------------------------------
# Rule 1: SPE_PRMS_INVALID_CATEGORY
# ---------------------------------------------------------------------------


class TestSPEPRMSInvalidCategory:
    def test_4p_is_invalid(self) -> None:
        violations = _check_spe_prms_invalid_category("Reserva 4P do Campo de Buzios")
        assert len(violations) == 1
        assert violations[0]["rule"] == "SPE_PRMS_INVALID_CATEGORY"
        assert "4P" in violations[0]["evidence"]

    def test_4p_case_insensitive(self) -> None:
        violations = _check_spe_prms_invalid_category("qual a reserva 4p?")
        assert any(v["rule"] == "SPE_PRMS_INVALID_CATEGORY" for v in violations)

    def test_1p_is_valid(self) -> None:
        violations = _check_spe_prms_invalid_category("A reserva 1P esta certificada.")
        assert len(violations) == 0

    def test_2p_is_valid(self) -> None:
        violations = _check_spe_prms_invalid_category("Reservas 2P do pre-sal.")
        assert len(violations) == 0

    def test_3p_is_valid(self) -> None:
        violations = _check_spe_prms_invalid_category("Estimativa de reservas 3P.")
        assert len(violations) == 0

    def test_5p_is_invalid(self) -> None:
        violations = _check_spe_prms_invalid_category("Reserva 5P nao existe.")
        assert any(v["rule"] == "SPE_PRMS_INVALID_CATEGORY" for v in violations)

    def test_suggested_fix_mentions_valid_categories(self) -> None:
        violations = _check_spe_prms_invalid_category("Reserva 4P")
        assert violations
        fix = violations[0]["suggested_fix"]
        assert "1P" in fix
        assert "2P" in fix
        assert "3P" in fix

    def test_no_false_positive_on_unrelated_text(self) -> None:
        violations = _check_spe_prms_invalid_category("O poco 3-BRSA-944-RJS foi perfurado.")
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# Rule 2: RESERVA_AMBIENTAL_CONFUSION
# ---------------------------------------------------------------------------


class TestReservaAmbientalConfusion:
    def test_flags_confusion_with_rebio(self) -> None:
        text = (
            "A reserva de hidrocarbonetos do campo tem 500 MMboe; "
            "a REBIO da regiao e protegida."
        )
        violations = _check_reserva_ambiental_confusion(text)
        assert any(v["rule"] == "RESERVA_AMBIENTAL_CONFUSION" for v in violations)

    def test_flags_confusion_with_rppn(self) -> None:
        text = (
            "Reservas provadas de oleo (1P) de 2 bilhoes de barris. "
            "A RPPN na area costeira nao pode ser explorada."
        )
        violations = _check_reserva_ambiental_confusion(text)
        assert any(v["rule"] == "RESERVA_AMBIENTAL_CONFUSION" for v in violations)

    def test_no_false_positive_oil_context_without_ambiental(self) -> None:
        text = "Reservas de gas natural estimadas em 300 bilhoes de m3 (1P)."
        violations = _check_reserva_ambiental_confusion(text)
        assert len(violations) == 0

    def test_no_false_positive_environmental_text_without_oil(self) -> None:
        text = "A REBIO do Guapore e uma reserva biologica federal."
        violations = _check_reserva_ambiental_confusion(text)
        assert len(violations) == 0

    def test_suggested_fix_distinguishes_contexts(self) -> None:
        text = "reservas de petroleo campo REBIO"
        violations = _check_reserva_ambiental_confusion(text)
        if violations:
            fix = violations[0]["suggested_fix"]
            assert "SPE-PRMS" in fix or "hidrocarbonetos" in fix
            assert "REBIO" in fix or "ambiental" in fix.lower()


# ---------------------------------------------------------------------------
# Rule 3: REGIME_CONTRATUAL_INVALID
# ---------------------------------------------------------------------------


class TestReimeContratual:
    def test_concessao_is_valid(self) -> None:
        violations = _check_regime_contratual("O bloco esta sob regime contratual de Concessão.")
        assert len(violations) == 0

    def test_partilha_is_valid(self) -> None:
        violations = _check_regime_contratual(
            "O campo opera sob regime de Partilha de Produção."
        )
        assert len(violations) == 0

    def test_cessao_onerosa_is_valid(self) -> None:
        violations = _check_regime_contratual(
            "Buzios esta sob Cessão Onerosa."
        )
        # Cessao Onerosa mentioned without "regime contratual" keyword may not trigger
        # — add the keyword to ensure the rule activates
        text = "O regime contratual do bloco e Cessão Onerosa."
        violations = _check_regime_contratual(text)
        assert len(violations) == 0

    def test_invalid_regime_is_flagged(self) -> None:
        violations = _check_regime_contratual(
            "O regime contratual e de servicos tecnicos."
        )
        assert any(v["rule"] == "REGIME_CONTRATUAL_INVALID" for v in violations)

    def test_suggested_fix_lists_valid_regimes(self) -> None:
        violations = _check_regime_contratual(
            "O regime contratual e servicos tecnicos."
        )
        if violations:
            fix = violations[0]["suggested_fix"]
            assert "Concessão" in fix or "Concessao" in fix
            assert "Partilha" in fix


# ---------------------------------------------------------------------------
# Rule 4: TIPO_POCO_ANP_INVALID
# ---------------------------------------------------------------------------


class TestTipoPococANP:
    def test_exploratorio_prefix_1_valid(self) -> None:
        violations = _check_tipo_poco_anp("Poco exploratório 1-RJS-702-RJ perfurado.")
        assert len(violations) == 0

    def test_desenvolvimento_prefix_7_valid(self) -> None:
        violations = _check_tipo_poco_anp("7-BUZ-5-RJS e um poco de desenvolvimento.")
        assert len(violations) == 0

    def test_avaliacao_prefix_2_valid(self) -> None:
        violations = _check_tipo_poco_anp("2-ANP-1-RJ e um poco de avaliacao.")
        assert len(violations) == 0

    def test_invalid_prefix_8_flagged(self) -> None:
        violations = _check_tipo_poco_anp("O poco 8-XYZ-100-RJ foi perfurado.")
        assert any(v["rule"] == "TIPO_POCO_ANP_INVALID" for v in violations)

    def test_invalid_prefix_5_flagged(self) -> None:
        violations = _check_tipo_poco_anp("O poco 5-ABC-200-SP nao existe.")
        assert any(v["rule"] == "TIPO_POCO_ANP_INVALID" for v in violations)

    def test_suggested_fix_lists_valid_prefixes(self) -> None:
        violations = _check_tipo_poco_anp("8-XYZ-100-RJ")
        if violations:
            fix = violations[0]["suggested_fix"]
            assert "1-" in fix
            assert "3-" in fix or "7-" in fix


# ---------------------------------------------------------------------------
# Integration: validator_node with AgentState
# ---------------------------------------------------------------------------


class TestValidatorNode:
    def test_4p_question_fails_validation(self) -> None:
        state: AgentState = {
            "question": "Qual a Reserva 4P do Campo de Buzios?",
            "iteration": 0,
        }
        result = validator_node(state)
        assert result["validation"]["valid"] is False
        rules = [v["rule"] for v in result["validation"]["violations"]]
        assert "SPE_PRMS_INVALID_CATEGORY" in rules

    def test_valid_question_passes(self) -> None:
        state: AgentState = {
            "question": "O que e um bloco exploratorio?",
            "iteration": 0,
        }
        result = validator_node(state)
        assert result["validation"]["valid"] is True
        assert result["validation"]["violations"] == []

    def test_state_keys_preserved(self) -> None:
        state: AgentState = {
            "question": "Reserva 4P",
            "classification": "validation",
            "iteration": 0,
        }
        result = validator_node(state)
        # Original keys must be preserved
        assert result["question"] == "Reserva 4P"
        assert result["classification"] == "validation"
        # New key added
        assert "validation" in result

    def test_draft_also_checked(self) -> None:
        """Violations in the draft (synthesizer output) are also caught."""
        state: AgentState = {
            "question": "O que sao reservas?",
            "draft": "As reservas 4P sao calculadas pela empresa.",
            "iteration": 0,
        }
        result = validator_node(state)
        assert result["validation"]["valid"] is False

    def test_iteration_counter_not_modified_by_validator(self) -> None:
        state: AgentState = {"question": "Teste", "iteration": 1}
        result = validator_node(state)
        assert result.get("iteration") == 1
