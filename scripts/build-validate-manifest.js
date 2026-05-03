#!/usr/bin/env node
"use strict";
/**
 * build-validate-manifest.js — Generates api/v1/validate-rules.json.
 *
 * Produces a static JSON manifest of all validation rules with PT/EN
 * descriptions, severity levels, and examples. Intended to be called from
 * generate.js as part of the standard regen pipeline.
 *
 * Usage: node scripts/build-validate-manifest.js
 */

const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "api", "v1", "validate-rules.json");

const RULES = [
  {
    id: "SPE_PRMS_INVALID_CATEGORY",
    description_pt:
      "Categoria SPE-PRMS inválida. Somente 1P, 2P, 3P (Reservas) e C1C, C2C, C3C (Recursos Contingentes) são válidas.",
    description_en:
      "Invalid SPE-PRMS category. Only 1P/2P/3P (Reserves) and C1C/C2C/C3C (Contingent Resources) are valid.",
    severity: "error",
    source_layer: "taxonomies/categoria_recurso_spe_prms",
    legal_basis: "SPE-PRMS 2018",
    examples_positive: [
      "Reservas 2P do Campo de Santos",
      "Recursos Contingentes C1C do Bloco BM-S-11",
    ],
    examples_negative: ["Reserva 4P do Campo de Búzios", "Reserva 5P do pré-sal"],
  },
  {
    id: "RESERVA_AMBIGUITY",
    description_pt:
      "Possível confusão entre 'Reserva' SPE-PRMS (volumes de hidrocarbonetos) e 'Reserva Ambiental' (REBIO/RPPN/APA). Sempre desambiguar.",
    description_en:
      "Potential confusion between SPE-PRMS 'Reserva' (hydrocarbon volumes) and environmental protected areas (REBIO/RPPN/APA). Always disambiguate.",
    severity: "warning",
    source_layer: "taxonomies/categoria_recurso_spe_prms",
    legal_basis: "SPE-PRMS 2018; SNUC Lei 9.985/2000",
    examples_positive: ["Reservas 1P do Campo de Campos", "RPPN na Bacia do São Francisco"],
    examples_negative: [
      "Reserva petrolífera próxima à REBIO Comboios",
      "Volume de reserva 2P dentro da APA do Pratigi",
    ],
  },
  {
    id: "REGIME_CONTRATUAL_INVALID",
    description_pt:
      "Regime contratual inválido. Deve ser um de: Concessão (Lei 9.478/1997), Partilha de Produção (Lei 12.351/2010), Cessão Onerosa (Lei 12.276/2010).",
    description_en:
      "Invalid contractual regime. Must be one of: Concessão, Partilha de Produção, Cessão Onerosa.",
    severity: "error",
    source_layer: "entity-graph/regime-contratual",
    legal_basis: "Lei 9.478/1997; Lei 12.351/2010; Lei 12.276/2010",
    examples_positive: [
      "Bloco em regime de Concessão",
      "Bloco pré-sal em Partilha de Produção",
      "Cessão Onerosa do Campo de Buzios",
    ],
    examples_negative: ["Bloco em regime de Privatização", "Regime contratual de Nacionalização"],
  },
  {
    id: "TIPO_POCO_INVALID",
    description_pt:
      "Código de poço ANP com prefixo inválido. Prefixos válidos: 1- (Exploratório), 2- (Avaliação), 3- ou 7- (Desenvolvimento), 4- ou 6- (Especial).",
    description_en:
      "Invalid ANP well code prefix. Valid: 1- (Exploratory), 2- (Appraisal), 3-/7- (Development), 4-/6- (Special).",
    severity: "error",
    source_layer: "taxonomies/tipo_poco",
    legal_basis: "ANP Resolução 25/2003",
    examples_positive: ["1-RJS-702-RJ", "7-BUZ-5-RJS", "3-NA-0001-RN"],
    examples_negative: ["9-BUZ-1-RJS", "5-ABC-100-SP"],
  },
  {
    id: "LITOLOGIA_INVALID",
    description_pt:
      "Litologia não reconhecida na taxonomia canônica (CGI/GeoSciML). Verificar enumeração válida.",
    description_en:
      "Lithology not found in canonical taxonomy (CGI/GeoSciML). Check valid enumeration.",
    severity: "warning",
    source_layer: "taxonomies/tipo_litologia",
    legal_basis: "CGI Simple Lithology 2016",
    examples_positive: ["Litologia: arenito", "Litologia: calcario", "Rocha tipo folhelho"],
    examples_negative: ["Litologia: xistosidade", "Litologia: rocha_inventada"],
  },
  {
    id: "JANELA_GERACAO_INVALID",
    description_pt:
      "Janela de geração não reconhecida. Valores válidos: imaturo, janela de óleo, gás úmido, gás seco, sobrematuro (escala Ro%).",
    description_en:
      "Unrecognized generation window. Valid: imaturo, janela de óleo, gás úmido, gás seco, sobrematuro (Ro% scale).",
    severity: "warning",
    source_layer: "taxonomies/janela_geracao",
    legal_basis: "SPE — Petroleum Systems (vitrinite reflectance scale)",
    examples_positive: ["A formação está na janela de óleo (Ro 0.6%)", "Querogênio sobrematuro"],
    examples_negative: ["Janela de metamorfismo", "Janela de diagênese avançada"],
  },
  {
    id: "ACRONYM_AMBIGUOUS",
    description_pt:
      "Sigla com múltiplos sentidos no domínio O&G usada sem contexto de desambiguação.",
    description_en:
      "Acronym with multiple meanings in the O&G domain used without disambiguation context.",
    severity: "warning",
    source_layer: "acronyms",
    legal_basis: null,
    examples_positive: [
      "PAD (Plano de Avaliação de Descobertas) do bloco BM-C-33",
      "BOP instalado no poço 1-RJS-702-RJ",
    ],
    examples_negative: ["O PAD foi aprovado pela ANP", "API do poço"],
  },
  {
    id: "OSDU_KIND_FORMAT",
    description_pt:
      "OSDU kind não segue o padrão canônico 'opendes:osdu:<domain>--<Type>:<major>.<minor>.<patch>'.",
    description_en:
      "OSDU kind does not follow canonical pattern 'opendes:osdu:<domain>--<Type>:<major>.<minor>.<patch>'.",
    severity: "error",
    source_layer: "entity-graph/osdu_kind",
    legal_basis: "OSDU Forum — Data Platform specification",
    examples_positive: [
      "opendes:osdu:master-data--Well:1.0.0",
      "opendes:osdu:master-data--Field:1.0.0",
    ],
    examples_negative: ["osdu:Well:1.0", "opendes:master-data--Well", "opendes:osdu:Well:1.0.0"],
  },
  {
    id: "LAYER_COVERAGE_MISMATCH",
    description_pt:
      "A entidade afirmada não tem cobertura na camada semântica especificada no contexto.",
    description_en:
      "The asserted entity does not have coverage in the semantic layer specified in context.",
    severity: "warning",
    source_layer: "entity-graph/geocoverage",
    legal_basis: null,
    examples_positive: [
      '{ "value": "poco em layer1", "context": { "entity_id": "poco", "layer": "layer1" } }',
    ],
    examples_negative: [
      '{ "value": "poco em layer9", "context": { "entity_id": "poco", "layer": "layer9" } }',
    ],
  },
];

function buildManifest() {
  return {
    meta: {
      version: "1.0.0",
      generated: new Date().toISOString(),
      description: "Semantic validator rules manifest — GeoBrain",
      total_rules: RULES.length,
      python_validator_mirror: "examples/langgraph-agent/nodes/validator.py",
    },
    rules: RULES,
  };
}

function main() {
  const manifest = buildManifest();
  const outDir = path.dirname(OUT);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(manifest, null, 2) + "\n", "utf8");
  process.stdout.write(`Written: ${OUT} (${RULES.length} rules)\n`);
}

main();

module.exports = { buildManifest, RULES };
