"""test_validator.py — Parametrized parity tests mirroring scripts/semantic-validator.js.

All rule IDs, evidence strings, and pass/fail expectations match the JS test
suite in tests/validator.test.js.
"""

import pytest
from geobrain import Report, Validator


@pytest.fixture(scope="module")
def v():
    return Validator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def has_violation(report: Report, rule_id: str) -> bool:
    return any(viol.rule == rule_id for viol in report.violations)


def has_warning(report: Report, rule_id: str) -> bool:
    return any(warn.rule == rule_id for warn in report.warnings)


# ---------------------------------------------------------------------------
# SPE_PRMS_INVALID_CATEGORY
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_rule",
    [
        ("Reserva 4P do Campo de Búzios", "SPE_PRMS_INVALID_CATEGORY"),
        ("Estimativa de 5P para o pré-sal", "SPE_PRMS_INVALID_CATEGORY"),
        ("Recursos avaliados como 6P na Bacia de Santos", "SPE_PRMS_INVALID_CATEGORY"),
    ],
)
def test_spe_prms_invalid_category_violations(v, text, expected_rule):
    report = v.validate(text)
    assert report.valid is False
    assert has_violation(report, expected_rule), f"Expected {expected_rule} in: {text!r}"


@pytest.mark.parametrize(
    "text",
    [
        "Reservas 1P certificadas do Campo de Santos",
        "Volume de Reservas 2P estimado em 500 MMboe",
        "Reservas 3P totais do campo de Libra",
        "Recursos Contingentes C1C do bloco BM-C-33",
        "C2C estimados no pré-sal da Bacia de Santos",
        "C3C do Campo de Búzios revisados em 2024",
    ],
)
def test_spe_prms_valid_categories_no_violation(v, text):
    report = v.validate(text)
    assert not has_violation(report, "SPE_PRMS_INVALID_CATEGORY"), (
        f"Should not flag valid category in: {text!r}"
    )


# ---------------------------------------------------------------------------
# RESERVA_AMBIGUITY
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "A reserva petrolífera 2P fica próxima à REBIO Comboios no campo de Espírito Santo",
        "Volume de reserva em barris próximo à RPPN do bloco exploratório",
    ],
)
def test_reserva_ambiguity_warning(v, text):
    report = v.validate(text)
    assert has_warning(report, "RESERVA_AMBIGUITY"), (
        f"Expected RESERVA_AMBIGUITY warning in: {text!r}"
    )


@pytest.mark.parametrize(
    "text",
    [
        "Reservas 2P do Campo de Campos estimadas em 1 bilhão de barris",
        "A REBIO Comboios é uma unidade de conservação federal",
    ],
)
def test_reserva_ambiguity_no_warning_clean_context(v, text):
    report = v.validate(text)
    assert not has_warning(report, "RESERVA_AMBIGUITY"), f"Should not warn for: {text!r}"


# ---------------------------------------------------------------------------
# REGIME_CONTRATUAL_INVALID
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_rule",
    [
        ("Bloco BS-500 em regime de Privatização", "REGIME_CONTRATUAL_INVALID"),
        ("regime de Nacionalização para blocos do pré-sal", "REGIME_CONTRATUAL_INVALID"),
    ],
)
def test_regime_contratual_invalid(v, text, expected_rule):
    report = v.validate(text)
    assert report.valid is False
    assert has_violation(report, expected_rule), f"Expected {expected_rule} in: {text!r}"


@pytest.mark.parametrize(
    "text",
    [
        "Bloco BS-500 em regime de Concessão",
        "Bloco em regime de Partilha de Produção na Bacia de Santos",
        "Campo sob regime de Cessão Onerosa",
    ],
)
def test_regime_contratual_valid(v, text):
    report = v.validate(text)
    assert not has_violation(report, "REGIME_CONTRATUAL_INVALID"), (
        f"Should accept valid regime in: {text!r}"
    )


# ---------------------------------------------------------------------------
# TIPO_POCO_INVALID
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "Poço 9-BUZ-1-RJS perfurado na Bacia de Santos",
        "Poço 5-ABC-100-SP registrado na ANP",
    ],
)
def test_tipo_poco_invalid(v, text):
    report = v.validate(text)
    assert report.valid is False
    assert has_violation(report, "TIPO_POCO_INVALID"), f"Expected TIPO_POCO_INVALID in: {text!r}"


@pytest.mark.parametrize(
    "text",
    [
        "Poço exploratório 1-RJS-702-RJ descobriu o pré-sal",
        "Poço de desenvolvimento 7-BUZ-5-RJS em Búzios",
    ],
)
def test_tipo_poco_valid(v, text):
    report = v.validate(text)
    assert not has_violation(report, "TIPO_POCO_INVALID"), (
        f"Should accept valid well code in: {text!r}"
    )


# ---------------------------------------------------------------------------
# LITOLOGIA_INVALID
# ---------------------------------------------------------------------------


def test_litologia_invalid_unknown(v):
    report = v.validate("Litologia: xistosidade no intervalo 2000-2500m")
    assert has_warning(report, "LITOLOGIA_INVALID"), (
        "Should warn for unknown lithology 'xistosidade'"
    )


@pytest.mark.parametrize(
    "text",
    [
        "Litologia: arenito na Formação Macaré",
        "Litologia: calcario do reservatório carbonático do pré-sal",
    ],
)
def test_litologia_valid_known(v, text):
    report = v.validate(text)
    assert not has_warning(report, "LITOLOGIA_INVALID"), (
        f"Should not warn for known lithology in: {text!r}"
    )


# ---------------------------------------------------------------------------
# JANELA_GERACAO_INVALID
# ---------------------------------------------------------------------------


def test_janela_geracao_valid_oleo(v):
    report = v.validate("O querogênio está na janela de óleo com Ro 0.7%")
    assert not has_warning(report, "JANELA_GERACAO_INVALID")


def test_janela_geracao_invalid_metamorfismo(v):
    report = v.validate("Maturidade térmica na janela de metamorfismo segundo vitrinita")
    assert has_warning(report, "JANELA_GERACAO_INVALID")


# ---------------------------------------------------------------------------
# ACRONYM_AMBIGUOUS
# ---------------------------------------------------------------------------


def test_acronym_ambiguous_pad_no_context(v):
    report = v.validate("O PAD foi submetido à ANP para análise")
    assert has_warning(report, "ACRONYM_AMBIGUOUS"), "Should warn for ambiguous PAD"


def test_acronym_ambiguous_pad_with_context(v):
    report = v.validate("O Plano de Avaliação de Descobertas foi submetido à ANP")
    assert not has_warning(report, "ACRONYM_AMBIGUOUS")


def test_acronym_ambiguous_uts_no_context(v):
    report = v.validate("As UTS devem ser revisadas antes da próxima rodada")
    assert has_warning(report, "ACRONYM_AMBIGUOUS")


# ---------------------------------------------------------------------------
# OSDU_KIND_FORMAT
# ---------------------------------------------------------------------------


def test_osdu_kind_malformed_missing_version(v):
    report = v.validate("Entidade opendes:osdu:master-data--Well sem versão")
    assert report.valid is False
    assert has_violation(report, "OSDU_KIND_FORMAT")


def test_osdu_kind_malformed_wrong_prefix(v):
    report = v.validate("Kind opendes:master-data--Well no catálogo")
    assert report.valid is False
    assert has_violation(report, "OSDU_KIND_FORMAT")


def test_osdu_kind_valid_well(v):
    report = v.validate("Entidade do tipo opendes:osdu:master-data--Well:1.0.0")
    assert not has_violation(report, "OSDU_KIND_FORMAT")
    assert report.valid is True


def test_osdu_kind_valid_field(v):
    report = v.validate("OSDU kind opendes:osdu:master-data--Field:1.0.0 para campos de petróleo")
    assert not has_violation(report, "OSDU_KIND_FORMAT")


# ---------------------------------------------------------------------------
# LAYER_COVERAGE_MISMATCH (structured claim)
# ---------------------------------------------------------------------------


def test_layer_coverage_mismatch_invalid_layer(v):
    claim = {"value": "poco em layer9", "context": {"entity_id": "poco", "layer": "layer9"}}
    report = v.validate(claim)
    assert has_warning(report, "LAYER_COVERAGE_MISMATCH"), (
        "Should warn for layer not in geocoverage"
    )


def test_layer_coverage_mismatch_valid_layer(v):
    claim = {"value": "poco em layer1", "context": {"entity_id": "poco", "layer": "layer1"}}
    report = v.validate(claim)
    assert not has_warning(report, "LAYER_COVERAGE_MISMATCH")


def test_layer_coverage_mismatch_no_context(v):
    claim = {"type": "text", "value": "Campo de Santos em produção"}
    report = v.validate(claim)
    assert not has_warning(report, "LAYER_COVERAGE_MISMATCH")


# ---------------------------------------------------------------------------
# INVALID_INPUT
# ---------------------------------------------------------------------------


def test_invalid_input_none(v):
    report = v.validate(None)  # type: ignore[arg-type]
    assert report.valid is False
    assert has_violation(report, "INVALID_INPUT")


def test_invalid_input_number(v):
    report = v.validate(42)  # type: ignore[arg-type]
    assert report.valid is False
    assert has_violation(report, "INVALID_INPUT")


# ---------------------------------------------------------------------------
# Valid no-violation case
# ---------------------------------------------------------------------------


def test_fully_valid_claim_no_violations(v):
    report = v.validate("Reservas 2P certificadas do Campo de Santos")
    assert report.valid is True
    assert report.violations == []


def test_report_bool_interface(v):
    report = v.validate("Reservas 1P do bloco exploratório")
    assert bool(report) is True  # valid claims are truthy

    report_bad = v.validate("Reserva 4P do Campo de Búzios")
    assert bool(report_bad) is False
