"use strict";
/**
 * semantic-validator.js — Standalone deterministic semantic validator.
 *
 * Pure Node.js (CommonJS), no external dependencies. Reads data files from
 * the project data/ directory and validates claims against canonical
 * enumerations. Mirrors and extends the Python validator at
 * examples/langgraph-agent/nodes/validator.py.
 *
 * Usage (module):
 *   const { validate } = require('./scripts/semantic-validator');
 *   const result = validate('Reserva 4P do Campo de Buzios');
 *
 * Returns:
 *   { valid: bool, violations: [{rule, severity, evidence, suggested_fix, source_layer}], warnings: [...] }
 */

const fs = require("node:fs");
const path = require("node:path");

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

const DATA_DIR = path.resolve(__dirname, "..", "data");

function loadJson(filename) {
  const p = path.join(DATA_DIR, filename);
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

// Loaded once at module init — deterministic, side-effect free after this.
const _taxonomies = loadJson("taxonomies.json");
const _entityGraph = loadJson("entity-graph.json");
const _ontopetro = loadJson("ontopetro.json");
const _full = loadJson("full.json");

// ---------------------------------------------------------------------------
// Canonical value sets derived from data files
// ---------------------------------------------------------------------------

// SPE-PRMS — from taxonomies.json categoria_recurso_spe_prms
const _VALID_SPE_PRMS_RESERVES = new Set(["1P", "2P", "3P"]);
const _VALID_SPE_PRMS_CONTINGENT = new Set(["C1C", "C2C", "C3C"]);
const _VALID_SPE_PRMS_ALL = new Set([..._VALID_SPE_PRMS_RESERVES, ..._VALID_SPE_PRMS_CONTINGENT]);

// Regime contratual — Lei 9.478/1997, Lei 12.351/2010, Lei 12.276/2010
const _VALID_REGIMES = new Set([
  "concessão",
  "concessao",
  "partilha de produção",
  "partilha de producao",
  "partilha",
  "cessão onerosa",
  "cessao onerosa",
]);

// Environmental reserve signals indicating SPE-PRMS vs ambiental confusion
const _AMBIENTAL_SIGNALS = [
  "rebio",
  "rppn",
  "apa ",
  " apa",
  "reserva ambiental",
  "reserva biologica",
  "reserva biológica",
  "reserva particular",
  "area de protecao",
  "área de proteção",
  "unidade de conservacao",
  "unidade de conservação",
  "snuc",
];

// Oil/gas context keywords for RESERVA_AMBIGUITY check
const _OIL_GAS_KEYWORDS = [
  "campo",
  "bloco",
  "petroleo",
  "petróleo",
  "gas",
  "gás",
  "boe",
  "mboe",
  "bboe",
  "spe",
  "prms",
  "oleo",
  "óleo",
  "barris",
  "hidrocarboneto",
  "producao",
  "produção",
  "1p",
  "2p",
  "3p",
  "c1c",
  "c2c",
  "c3c",
  "provadas",
  "provaveis",
  "contingentes",
  "mmb",
  "bcf",
  "reservatorio",
  "reservatório",
];

// ANP well-type canonical prefixes — from taxonomies.json tipo_poco
const _ANP_WELL_PREFIXES = new Set(["1", "2", "3", "4", "6", "7"]);

// Lithology canonical values — from taxonomies.json tipo_litologia
function _buildLithologySet() {
  if (!_taxonomies || !_taxonomies.taxonomies || !_taxonomies.taxonomies.tipo_litologia) {
    return new Set([
      "arenito",
      "conglomerado",
      "folhelho",
      "argilito",
      "calcario",
      "dolomito",
      "marga",
      "siliciclastico",
      "carbonatico",
    ]);
  }
  const values = _taxonomies.taxonomies.tipo_litologia.values;
  const result = new Set();
  for (const [key, cat] of Object.entries(values)) {
    result.add(key);
    if (Array.isArray(cat.children)) {
      for (const child of cat.children) result.add(child);
    }
  }
  return result;
}
const _VALID_LITHOLOGIES = _buildLithologySet();

// Kerogen types — from taxonomies.json tipo_querogeno
function _buildKerogenSet() {
  if (!_taxonomies || !_taxonomies.taxonomies || !_taxonomies.taxonomies.tipo_querogeno) {
    return new Set([
      "tipo_i",
      "tipo_ii",
      "tipo_iis",
      "tipo_iii",
      "tipo_iv",
      "tipo i",
      "tipo ii",
      "tipo iii",
      "tipo iv",
    ]);
  }
  const values = _taxonomies.taxonomies.tipo_querogeno.values;
  const result = new Set();
  for (const key of Object.keys(values)) {
    result.add(key.toLowerCase());
    result.add(key.toLowerCase().replace("_", " "));
  }
  return result;
}
const _VALID_KEROGEN_TYPES = _buildKerogenSet();

// Generation window IDs — from taxonomies.json janela_geracao
function _buildWindowSet() {
  if (!_taxonomies || !_taxonomies.taxonomies || !_taxonomies.taxonomies.janela_geracao) {
    return new Set([
      "imaturo",
      "janela_oleo",
      "janela de óleo",
      "gas_umido",
      "gas_seco",
      "sobrematuro",
    ]);
  }
  const values = _taxonomies.taxonomies.janela_geracao.values;
  const result = new Set();
  for (const v of values) {
    result.add(v.id.toLowerCase());
    result.add(v.label.toLowerCase());
  }
  return result;
}
const _VALID_WINDOWS = _buildWindowSet();

// OSDU kind pattern — opendes:osdu:<domain>--<Type>:<version>
const _OSDU_KIND_REGEX = /^opendes:osdu:[a-z-]+--[A-Z][a-zA-Z]+:\d+\.\d+\.\d+$/;

// Entity layer map — built from entity-graph.json
function _buildEntityLayerMap() {
  const map = {};
  if (!_entityGraph || !_entityGraph.nodes) return map;
  for (const node of _entityGraph.nodes) {
    if (node.id && Array.isArray(node.geocoverage)) {
      map[node.id] = new Set(node.geocoverage);
    }
  }
  return map;
}
const _ENTITY_LAYER_MAP = _buildEntityLayerMap();

// Acronym map — sigla -> array of meanings (to detect ambiguous ones)
function _buildAcronymMap() {
  const map = {};
  const source = _full && _full.acronyms ? _full.acronyms : [];
  for (const a of source) {
    const sigla = a.sigla.toUpperCase();
    if (!map[sigla]) map[sigla] = [];
    map[sigla].push({
      expansion_pt: a.expansion_pt,
      expansion_en: a.expansion_en,
      category: a.category,
    });
  }
  return map;
}
const _ACRONYM_MAP = _buildAcronymMap();

// Known ambiguous acronyms from the ontopetro ambiguity_alerts
const _KNOWN_AMBIGUOUS = new Set(["PAD", "UTS", "GAS", "GÁS", "APA", "BOP", "API", "LWD", "MWD"]);

// ---------------------------------------------------------------------------
// Rule implementations
// ---------------------------------------------------------------------------

/**
 * SPE_PRMS_INVALID_CATEGORY — only 1P/2P/3P and C1C/C2C/C3C are valid.
 */
function _checkSpePromsInvalidCategory(text) {
  const violations = [];

  // Flag 4P explicitly
  if (/\b4\s*[Pp]\b/.test(text)) {
    violations.push({
      rule: "SPE_PRMS_INVALID_CATEGORY",
      severity: "error",
      evidence: "Menção a '4P' no texto.",
      suggested_fix:
        "A classificação SPE-PRMS não reconhece '4P'. " +
        "Categorias válidas para Reservas: 1P (Provadas), 2P (Prováveis), 3P (Possíveis). " +
        "Para Recursos Contingentes: C1C, C2C, C3C.",
      source_layer: "taxonomies/categoria_recurso_spe_prms",
    });
  }

  // Flag other bogus reserve codes 5P, 6P, etc.
  const bogusRe = /\b([5-9][Pp]|[1-9][0-9]+[Pp])\b/g;
  let m;
  while ((m = bogusRe.exec(text)) !== null) {
    const label = m[1].toUpperCase();
    violations.push({
      rule: "SPE_PRMS_INVALID_CATEGORY",
      severity: "error",
      evidence: `Menção a '${label}' no texto.`,
      suggested_fix:
        `'${label}' não é uma categoria SPE-PRMS válida. ` +
        "Categorias válidas para Reservas: 1P, 2P, 3P.",
      source_layer: "taxonomies/categoria_recurso_spe_prms",
    });
  }

  return violations;
}

/**
 * RESERVA_AMBIGUITY — flags "Reserva" near environmental terms
 * to distinguish SPE-PRMS reserva from reserva ambiental.
 */
function _checkReservaAmbiguity(text) {
  const violations = [];
  const lower = text.toLowerCase();

  const hasReserva = lower.includes("reserva");
  const hasOilContext = _OIL_GAS_KEYWORDS.some((kw) => lower.includes(kw));
  const hasAmbientalSignal = _AMBIENTAL_SIGNALS.some((sig) => lower.includes(sig));

  if (hasReserva && hasAmbientalSignal && hasOilContext) {
    violations.push({
      rule: "RESERVA_AMBIGUITY",
      severity: "warning",
      evidence:
        "O texto menciona 'reserva' em contexto de petróleo/gás " +
        "mas também contém termos de reserva ambiental (REBIO, RPPN, APA, etc.).",
      suggested_fix:
        "Desambiguar: 'Reserva' no contexto SPE-PRMS refere-se a volumes de hidrocarbonetos " +
        "tecnicamente recuperáveis e comercialmente viáveis (1P/2P/3P). " +
        "'Reserva Ambiental' (REBIO/RPPN/APA) é uma área de proteção ambiental " +
        "regulada pelo SNUC (Lei 9.985/2000) e não tem relação com volumes petrolíferos.",
      source_layer: "taxonomies/categoria_recurso_spe_prms",
    });
  }

  return violations;
}

/**
 * REGIME_CONTRATUAL_INVALID — must be Concessão, Partilha de Produção, or Cessão Onerosa.
 */
function _checkRegimeContratual(text) {
  const violations = [];
  const lower = text.toLowerCase();

  const regimeKeywords = [
    "regime contratual",
    "regime de",
    "modalidade contratual",
    "regime explorat",
    "contrato de",
  ];
  if (!regimeKeywords.some((kw) => lower.includes(kw))) return violations;

  // Match both "regime contratual de X" and "regime de X".
  // Strategy: extract a greedy 1-4 word block then split on the first preposition
  // or article that would start a new phrase.
  const rawMatch = text.match(
    /regime\s+(?:contratual\s+)?(?:(?:é|e|de|em)\s+(?:o\s+)?|:\s*)([A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+(?:\s+[A-Za-záéíóúâêîôûàãõçÁÉÍÓÚÂÊÎÔÛÀÃÕÇ]+){0,3})/i
  );
  // Trim the candidate at the first preposition / article boundary.
  // Prepositions allowed inside regime names: "de" (Partilha de Produção), "Onerosa".
  // Prepositions that start a new phrase: para, com, nos, nas, no, na, em (standalone).
  const _BOUNDARY_RE =
    /\s+(?:para|com|nos|nas|no|na|sobre|entre|até|pelos?|pelas?|num|numa|pelo)\b/i;
  let match = null;
  if (rawMatch) {
    const trimmed = rawMatch[1].replace(_BOUNDARY_RE, "").trim();
    match = trimmed ? [rawMatch[0], trimmed] : null;
  }

  if (match) {
    const candidate = match[1].trim().toLowerCase();
    if (candidate && !_VALID_REGIMES.has(candidate)) {
      violations.push({
        rule: "REGIME_CONTRATUAL_INVALID",
        severity: "error",
        evidence: `Regime contratual mencionado: '${candidate}'.`,
        suggested_fix:
          "Regimes contratuais válidos no Brasil: " +
          "Concessão (Lei 9.478/1997), " +
          "Partilha de Produção (Lei 12.351/2010), " +
          "Cessão Onerosa (Lei 12.276/2010).",
        source_layer: "entity-graph/regime-contratual",
      });
    }
  }

  return violations;
}

/**
 * TIPO_POCO_INVALID — checks ANP well code prefix against canonical enumeration.
 */
function _checkTipoPocoInvalid(text) {
  const violations = [];
  const codeRe = /\b([0-9])-[A-Z]{2,4}-[0-9]+-[A-Z]{2,4}\b/g;
  let m;
  while ((m = codeRe.exec(text)) !== null) {
    const fullCode = m[0];
    const prefix = m[1];
    if (!_ANP_WELL_PREFIXES.has(prefix)) {
      violations.push({
        rule: "TIPO_POCO_INVALID",
        severity: "error",
        evidence: `Código de poço ANP '${fullCode}' com prefixo '${prefix}-' desconhecido.`,
        suggested_fix:
          "Prefixos ANP válidos: " +
          "1- (Exploratório), 2- (Avaliação), " +
          "3- ou 7- (Desenvolvimento), 4- ou 6- (Especial).",
        source_layer: "taxonomies/tipo_poco",
      });
    }
  }
  return violations;
}

/**
 * LITOLOGIA_INVALID — checks lithology terms against canonical taxonomy.
 */
function _checkLitologiaInvalid(text) {
  const violations = [];
  const lower = text.toLowerCase();

  // Only run if the claim is about lithology
  const litKeywords = [
    "litologia",
    "litológic",
    "litologic",
    "rocha",
    "lithology",
    "tipo de rocha",
    "fácies",
  ];
  if (!litKeywords.some((kw) => lower.includes(kw))) return violations;

  // Extract candidate lithology term after trigger phrases.
  // Stop at whitespace followed by a preposition / article to avoid over-capture.
  const triggerRe = /(?:litologia|tipo de rocha|lithology)[:\s]+([a-záéíóúâêîôûàãõç]+)/gi;
  let m;
  while ((m = triggerRe.exec(lower)) !== null) {
    const candidate = m[1].trim();
    const candidateUnderscored = candidate.replace(/\s+/g, "_");
    if (!_VALID_LITHOLOGIES.has(candidate) && !_VALID_LITHOLOGIES.has(candidateUnderscored)) {
      violations.push({
        rule: "LITOLOGIA_INVALID",
        severity: "warning",
        evidence: `Litologia '${candidate}' não reconhecida na taxonomia canônica.`,
        suggested_fix: `Litologias válidas (taxonomia CGI/GeoSciML): ${Array.from(_VALID_LITHOLOGIES).join(", ")}.`,
        source_layer: "taxonomies/tipo_litologia",
      });
    }
  }

  return violations;
}

/**
 * JANELA_GERACAO_INVALID — querogênio/janela enumerations.
 */
function _checkJanelaGeracaoInvalid(text) {
  const violations = [];
  const lower = text.toLowerCase();

  const janelaKeywords = [
    "janela de geração",
    "janela de geracao",
    "janela de maturação",
    "maturidade termica",
    "maturidade térmica",
    "vitrinita",
    "querogênio",
    "querogênio",
  ];
  if (!janelaKeywords.some((kw) => lower.includes(kw))) return violations;

  // Extract candidate window after "janela de".
  // Strategy: extract one word, then optionally extend to two words only when the
  // two-word form is actually in the valid set. This avoids over-capturing
  // "janela de óleo com Ro..." as "óleo com".
  const windowRe = /janela\s+de\s+([a-záéíóúâêîôûàãõç]+)(?:\s+([a-záéíóúâêîôûàãõç]+))?/gi;
  let m;
  while ((m = windowRe.exec(lower)) !== null) {
    const word1 = m[1];
    const word2 = m[2];
    // Prefer the two-word form if it is in the valid set
    let candidate = word1;
    if (word2) {
      const twoWords = `${word1} ${word2}`;
      if (_VALID_WINDOWS.has(twoWords) || _VALID_WINDOWS.has(`janela de ${twoWords}`)) {
        candidate = twoWords;
      }
    }
    const windowLabel = `janela de ${candidate}`;
    if (!_VALID_WINDOWS.has(candidate) && !_VALID_WINDOWS.has(windowLabel)) {
      violations.push({
        rule: "JANELA_GERACAO_INVALID",
        severity: "warning",
        evidence: `Janela de geração '${candidate}' não reconhecida.`,
        suggested_fix:
          `Janelas válidas: ${Array.from(_VALID_WINDOWS).join(", ")}. ` +
          "Baseadas na reflectância da vitrinita (Ro%).",
        source_layer: "taxonomies/janela_geracao",
      });
    }
  }

  return violations;
}

/**
 * ACRONYM_AMBIGUOUS — sigla with multiple senses must include disambiguation context.
 */
function _checkAcronymAmbiguous(text) {
  const violations = [];
  const upper = text.toUpperCase();

  // Match 2-6 letter uppercase acronyms that appear as standalone words
  const siglaRe = /\b([A-Z]{2,6})\b/g;
  const seen = new Set();
  let m;
  while ((m = siglaRe.exec(upper)) !== null) {
    const sigla = m[1];
    if (seen.has(sigla)) continue;
    seen.add(sigla);

    if (!_KNOWN_AMBIGUOUS.has(sigla)) continue;

    // Check if acronym map has multiple categories for this sigla
    const entries = _ACRONYM_MAP[sigla];
    const isAmbiguous = entries && entries.length > 1;
    const isKnownAmbiguous = _KNOWN_AMBIGUOUS.has(sigla);

    if (isAmbiguous || isKnownAmbiguous) {
      // Only flag if there is no obvious disambiguation in surrounding context
      const contextWindow = text.toLowerCase();
      const hasContext = [
        "plano de avaliacao",
        "plano de avaliação",
        "drilling pad",
        "pad explorat",
        "unidades de trabalho",
        "unidade territorial",
        "api gravity",
        "api grau",
        "bloqueador de poc",
        "blowout preventer",
      ].some((ctx) => contextWindow.includes(ctx));

      if (!hasContext) {
        const meanings = entries
          ? entries
              .map((e) => e.expansion_pt || e.expansion_en)
              .filter(Boolean)
              .join(" / ")
          : "(múltiplos sentidos)";
        violations.push({
          rule: "ACRONYM_AMBIGUOUS",
          severity: "warning",
          evidence: `Sigla '${sigla}' tem múltiplos sentidos no domínio O&G: ${meanings}.`,
          suggested_fix:
            `Incluir contexto de desambiguação ao usar '${sigla}'. ` +
            "Exemplo: especificar se é o sentido regulatório (ANP), operacional ou geomecânico.",
          source_layer: "acronyms",
        });
      }
    }
  }

  return violations;
}

/**
 * OSDU_KIND_FORMAT — must match opendes:osdu:<domain>--<Type>:<version>.
 */
function _checkOsduKindFormat(text) {
  const violations = [];

  // Find anything that looks like an OSDU kind (contains "osdu:" or "opendes:")
  const kindRe = /\bopendes:[^\s,;'"]+|osdu:[a-z-]+--[A-Za-z][^\s,;'"]+/g;
  let m;
  while ((m = kindRe.exec(text)) !== null) {
    const candidate = m[0];
    if (!_OSDU_KIND_REGEX.test(candidate)) {
      violations.push({
        rule: "OSDU_KIND_FORMAT",
        severity: "error",
        evidence: `OSDU kind '${candidate}' não segue o padrão canônico.`,
        suggested_fix:
          "Formato correto: 'opendes:osdu:<domain>--<Type>:<major>.<minor>.<patch>'. " +
          "Exemplo: 'opendes:osdu:master-data--Well:1.0.0'.",
        source_layer: "entity-graph/osdu_kind",
      });
    }
  }

  return violations;
}

/**
 * LAYER_COVERAGE_MISMATCH — claim asserts entity in layer X but geocoverage doesn't include X.
 */
function _checkLayerCoverageMismatch(claim) {
  const violations = [];

  if (typeof claim !== "object" || claim === null) return violations;

  const { value, context } = claim;
  if (!value || !context) return violations;

  const entityId = (context.entity_id || "").toLowerCase().replace(/\s+/g, "-");
  const assertedLayer = context.layer;

  if (!entityId || !assertedLayer) return violations;

  const coverage = _ENTITY_LAYER_MAP[entityId];
  if (!coverage) return violations;

  if (!coverage.has(assertedLayer)) {
    violations.push({
      rule: "LAYER_COVERAGE_MISMATCH",
      severity: "warning",
      evidence:
        `Entidade '${entityId}' não tem cobertura na camada '${assertedLayer}'. ` +
        `Camadas cobertas: ${Array.from(coverage).join(", ")}.`,
      suggested_fix:
        `Verificar a cobertura da entidade '${entityId}' no entity-graph.json. ` +
        `A camada '${assertedLayer}' não está no campo geocoverage desta entidade.`,
      source_layer: "entity-graph/geocoverage",
    });
  }

  return violations;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Validate a claim.
 *
 * @param {string|{type?: string, value: string, context?: object}} claim
 *   - string: free text to validate
 *   - object: structured claim with .value (text) and optional .context for
 *     LAYER_COVERAGE_MISMATCH and similar structured rules
 * @returns {{ valid: boolean, violations: Array, warnings: Array }}
 */
function validate(claim) {
  let text = "";
  let structuredClaim = null;

  if (typeof claim === "string") {
    text = claim;
  } else if (claim && typeof claim === "object") {
    text = claim.value || "";
    structuredClaim = claim;
  } else {
    return {
      valid: false,
      violations: [
        {
          rule: "INVALID_INPUT",
          severity: "error",
          evidence: "claim must be a string or object with .value",
          suggested_fix: "Pass a string or { type, value, context }.",
          source_layer: "validator",
        },
      ],
      warnings: [],
    };
  }

  const allViolations = [
    ..._checkSpePromsInvalidCategory(text),
    ..._checkReservaAmbiguity(text),
    ..._checkRegimeContratual(text),
    ..._checkTipoPocoInvalid(text),
    ..._checkLitologiaInvalid(text),
    ..._checkJanelaGeracaoInvalid(text),
    ..._checkAcronymAmbiguous(text),
    ..._checkOsduKindFormat(text),
    ...(structuredClaim ? _checkLayerCoverageMismatch(structuredClaim) : []),
  ];

  const violations = allViolations.filter((v) => v.severity === "error");
  const warnings = allViolations.filter((v) => v.severity === "warning");

  return {
    valid: violations.length === 0,
    violations,
    warnings,
  };
}

module.exports = { validate };
