#!/usr/bin/env node
/**
 * generate.js — Regenera /data, /api e /ai a partir dos arquivos-fonte do Geolytics.
 *
 * Os dados (GLOSSARIO, CONJUNTOS, ONTOLOGY) ficam embedados aqui para tornar o
 * script standalone. Se quiser sincronizar com o Geolytics, copie os exports
 * de:
 *   src/config/dicionario.js  → GLOSSARIO, CONJUNTOS
 *   src/config/ontology.js    → ONTOLOGY
 *
 * Uso: node scripts/generate.js
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { extractGSO } from "./gso-extract.js";
import {
  PETROKGRAPH_BASE,
  TERM_ALIGNMENT,
  TERM_ENRICHMENT,
  EXTENDED_TERMS,
  ENTITY_ALIGNMENT,
  LAYER_DEFINITIONS,
  DEDUP_RULES,
  RECOMMENDED_USAGE,
} from "./ontology-alignment.js";
import { OSDU_CANONICAL } from "./osdu-canonical.js";
import { buildTtl } from "./ttl-serializer.js";
import { buildCardsHtml, buildGsoCardsHtml } from "./cards-html.js";
import { OSDU_EXTRA_NODES, OSDU_EXTRA_EDGES, OSDU_EXTRA_ALIGNMENT } from "./osdu-extra-nodes.js";
import { OG_NODES, OG_EDGES, OG_GLOSSARY } from "./operacoes-geologicas-nodes.js";
import {
  GPP_NODES,
  GPP_EDGES,
  GPP_GLOSSARY,
  GPP_NODE_PATCHES,
} from "./gestao-projetos-parcerias-nodes.js";
import {
  THREEW_VARIABLES,
  THREEW_EQUIPMENT,
  THREEW_EQUIPMENT_PATCHES,
  THREEW_EVENTS,
  THREEW_EDGES,
  THREEW_TAXONOMIES,
  THREEW_DATASET,
  THREEW_ACRONYM_LINKS,
  THREEW_RAG_CHUNKS,
} from "./threew-data.js";
import {
  ONTOPETRO_CLASSES,
  ONTOPETRO_PROPERTIES,
  ONTOPETRO_RELATIONS,
  ONTOPETRO_INSTANCES,
  TAXONOMIES,
  MODULES_EXTENDED,
  PVT_FIELDS,
  SYSTEMS,
  REGIS_NER_MAPPINGS,
  REGIS_RELATION_TYPES,
  ONTOPETRO_NODES,
  ONTOPETRO_EDGES,
  ONTOPETRO_ALIGNMENT,
  AMBIGUITY_ALERTS,
  OSDU_NODES,
  OSDU_EDGES,
  OSDU_ALIGNMENT_ADDITIONS,
  OSDU_RAG_CHUNKS,
} from "./ontopetro-data.js";

/* 3W integration: extend TAXONOMIES with 3W entries */
Object.assign(TAXONOMIES, THREEW_TAXONOMIES);

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const DRY_RUN = process.argv.includes("--dry-run");

/* SWEET alignment — load synchronously from data/sweet-alignment.json.
   Returns a Map<geolytics_id, alignment[]> used by buildTtl. */
/**
 * Loads the SWEET ontology alignment file (`data/sweet-alignment.json`)
 * synchronously and returns a Map keyed by `geolytics_id`. Returns an empty
 * Map if the file does not exist or cannot be parsed.
 *
 * @returns {Map<string, Array<{sweet_uris: string[], alignment_type: string, sweet_module: string}>>}
 */
function loadSweetAlignmentSync() {
  try {
    const candidate = path.join(ROOT, "data", "sweet-alignment.json");
    if (!fs.existsSync(candidate)) return new Map();
    const data = JSON.parse(fs.readFileSync(candidate, "utf8"));
    const alignments = Array.isArray(data?.alignments) ? data.alignments : [];
    const map = new Map();
    for (const a of alignments) {
      if (!a.geolytics_id) continue;
      const existing = map.get(a.geolytics_id) || [];
      existing.push(a);
      map.set(a.geolytics_id, existing);
    }
    return map;
  } catch {
    return new Map();
  }
}

/**
 * Returns the ontology alignment data for a given entity-graph node ID,
 * resolving the Petro KGraph fragment to a full URI and normalising absent
 * fields to null. Falls back to all-null when the ID is not present in
 * the supplied table.
 *
 * @param {Object.<string, {kg: string|null, osdu: string|null, gsml?: string, layers?: string[]}>} table - Alignment table (e.g. ENTITY_ALIGNMENT, ONTOPETRO_ALIGNMENT)
 * @param {string} id - Entity-graph node identifier (e.g. 'poco', 'formacao')
 * @returns {{petrokgraph_uri: string|null, osdu_kind: string|null, geosciml_uri: string|null, geocoverage: string[]}}
 */
function alignmentFor(table, id) {
  const a = table[id];
  if (!a) return { petrokgraph_uri: null, osdu_kind: null, geosciml_uri: null, geocoverage: [] };
  return {
    petrokgraph_uri: a.kg ? `${PETROKGRAPH_BASE}${a.kg}` : null,
    osdu_kind: a.osdu,
    geosciml_uri: a.gsml || null,
    geocoverage: a.layers || [],
  };
}

/**
 * Looks up OSDU canonical metadata (OWL URI and English definition) for a
 * given OSDU kind string using the OSDU_CANONICAL lookup table from
 * `scripts/osdu-canonical.js`. Returns null fields when the kind is absent
 * or null.
 *
 * @param {string|null} kind - OSDU kind string (e.g. 'opendes:osdu:master-data--Well:1.0.0')
 * @returns {{owl_uri: string|null, definition_en_canonical: string|null, osdu_class?: string, osdu_canonical_note?: string}}
 */
function osduCanonical(kind) {
  if (!kind) return { owl_uri: null, definition_en_canonical: null };
  const c = OSDU_CANONICAL[kind];
  if (!c) return { owl_uri: null, definition_en_canonical: null };
  return {
    owl_uri: c.owl_uri || null,
    definition_en_canonical: c.definition_en_canonical || null,
    osdu_class: c.osdu_class || null,
    osdu_canonical_note: c.note || null,
  };
}

/**
 * Augments an entity-graph node object with SKOS-named alias fields
 * (`skos_prefLabel`, `skos_altLabel`, `skos_definition`, `skos_example`) for
 * direct interoperability with rdflib, Protégé, and GraphDB consumers.
 *
 * @param {{label: string, label_en: string, definition: string, definition_en_canonical?: string, synonyms_pt?: string[], synonyms_en?: string[], examples?: string[]}} node
 * @returns {Object} The input node extended with SKOS alias fields
 */
function withSkosAliases(node) {
  return {
    ...node,
    skos_prefLabel: { "@pt": node.label, "@en": node.label_en },
    skos_altLabel: { "@pt": node.synonyms_pt || [], "@en": node.synonyms_en || [] },
    skos_definition: { "@pt": node.definition, "@en": node.definition_en_canonical || null },
    skos_example: node.examples || [],
  };
}

function enrichmentFor(id) {
  return TERM_ENRICHMENT[id] || { termo_en: null, synonyms_pt: [], synonyms_en: [], examples: [] };
}

/**
 * Loads all GSO (Loop3D Geoscience Ontology) JSON files from the `data/`
 * directory. Files are matched by the pattern `gso-<name>.json` and were
 * produced by `scripts/gso-extract.js`. Returns an empty array when the
 * data directory does not exist.
 *
 * @returns {Array<{file: string, meta: Object, classes: Object}>} Parsed GSO module objects
 */
function loadGsoModules() {
  const dataDir = path.resolve(__dirname, "..", "data");
  if (!fs.existsSync(dataDir)) return [];
  return fs
    .readdirSync(dataDir)
    .filter((f) => /^gso-[a-z]+\.json$/.test(f))
    .map((f) => {
      const json = JSON.parse(fs.readFileSync(path.join(dataDir, f), "utf8"));
      return { file: f, ...json };
    });
}
/* ─────────────────────────────────────────────────────────────
 * SEISMIC MODULE (P2.8) — Aquisicao, Processamento, Inversao
 * Sources: Yilmaz 2001, Sheriff & Geldart 1995, Russell 1988,
 *   Connolly 1999, Chopra & Marfurt 2007, Coleou et al. 2003
 * ───────────────────────────────────────────────────────────── */

function loadSeismicModules() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const files = [
    "seismic-acquisition.json",
    "seismic-processing.json",
    "seismic-inversion-attributes.json",
  ];
  return files
    .map((f) => {
      const p = path.join(dataDir, f);
      if (!fs.existsSync(p)) {
        console.warn(`  [warn] Seismic file not found, skipping: ${f}`);
        return null;
      }
      return JSON.parse(fs.readFileSync(p, "utf8"));
    })
    .filter(Boolean);
}

/**
 * Consolidates all seismic module JSON files into a single object for
 * `api/v1/seismic.json`. Merges classes, properties, relations, and instances
 * from `data/seismic-acquisition.json`, `data/seismic-processing.json`, and
 * `data/seismic-inversion-attributes.json`.
 *
 * @returns {{meta: Object, modules: Object[], classes: Object, properties: Object, relations: Object, instances: Object}}
 */
function buildSeismicConsolidated() {
  const modules = loadSeismicModules();
  const allClasses = {};
  const allProperties = {};
  const allRelations = {};
  const allInstances = {};
  for (const m of modules) {
    Object.assign(allClasses, m.classes || {});
    Object.assign(allProperties, m.properties || {});
    Object.assign(allRelations, m.relations || {});
    Object.assign(allInstances, m.instances || {});
  }
  return {
    meta: {
      version: "1.0.0",
      generated: NOW,
      description:
        "Geolytics Seismic Module — consolidated acquisition, processing, inversion and attributes",
      module_count: modules.length,
      class_count: Object.keys(allClasses).length,
      property_count: Object.keys(allProperties).length,
      relation_count: Object.keys(allRelations).length,
      instance_count: Object.keys(allInstances).length,
      sources: [
        "Yilmaz, O. (2001). Seismic Data Analysis. SEG Investigations in Geophysics No. 10.",
        "Sheriff, R.E. & Geldart, L.P. (1995). Exploration Seismology. Cambridge University Press.",
        "Russell, B.H. (1988). Introduction to Seismic Inversion Methods. SEG Course Notes.",
        "Connolly, P. (1999). Elastic Impedance. The Leading Edge, 18(4), 438-452.",
        "Chopra, S. & Marfurt, K.J. (2007). Seismic Attributes. SEG.",
        "Coleou, T. et al. (2003). Unsupervised seismic facies classification. The Leading Edge.",
        "OSDU SeismicAcquisitionSurvey / SeismicProcessingProject / SeismicTraceData schemas v1.0.0",
      ],
    },
    modules: modules.map((m) => m.meta),
    classes: allClasses,
    properties: allProperties,
    relations: allRelations,
    instances: allInstances,
  };
}

/**
 * Produces RAG corpus chunks for seismic acquisition, processing, and
 * inversion/attribute modules. Emits `seismic_class`, `seismic_attribute`,
 * and `seismic_property` chunk types. High-priority properties and
 * DHI/AVO attribute subclasses receive dedicated chunks.
 *
 * @returns {Array<{id: string, type: string, text: string, metadata: Object}>}
 */
function buildSeismicRagChunks() {
  const modules = loadSeismicModules();
  const lines = [];
  for (const m of modules) {
    const moduleName = m.meta.module;
    for (const [key, c] of Object.entries(m.classes || {})) {
      const text = `Seismic class "${c.name}" (${c.name_pt || c.name}, superclass ${c.superclass || "owl:Thing"}): ${c.description || ""}${c.osdu_kind ? ` OSDU kind: ${c.osdu_kind}.` : ""} Sources: ${(c.sources || []).join(", ")}.`;
      lines.push({
        id: `seismic_class_${moduleName}_${key}`,
        type: "seismic_class",
        text,
        metadata: {
          id: key,
          name: c.name,
          module: moduleName,
          superclass: c.superclass || "owl:Thing",
          osdu_kind: c.osdu_kind || null,
        },
      });
    }
    for (const [key, c] of Object.entries(m.classes || {})) {
      if (!c.superclass || !["SeismicAttribute", "DHI", "AVOAnomaly"].includes(c.superclass))
        continue;
      const text = `Seismic attribute "${c.name}" (${c.name_pt || c.name}): ${c.description || ""} Sources: ${(c.sources || []).join(", ")}.`;
      lines.push({
        id: `seismic_attribute_${moduleName}_${key}`,
        type: "seismic_attribute",
        text,
        metadata: { id: key, name: c.name, module: moduleName, attribute_superclass: c.superclass },
      });
    }
    for (const [key, p] of Object.entries(m.properties || {})) {
      if (p.rag_priority !== "high") continue;
      const text = `Seismic property "${p.name}" (${p.name_pt || p.name}): ${p.description || ""} Unit: ${p.unit || "n/a"}.`;
      lines.push({
        id: `seismic_property_${moduleName}_${key}`,
        type: "seismic_class",
        text,
        metadata: { id: key, name: p.name, unit: p.unit, module: moduleName },
      });
    }
    for (const [key, i] of Object.entries(m.instances || {})) {
      const attrs = Object.entries(i.attributes || {})
        .slice(0, 8)
        .map(([k, v]) => `${k}: ${v}`)
        .join("; ");
      const text = `Seismic instance (${i.id}) "${i.name}" — class ${i.class}. ${i.description || ""}${attrs ? ` Attributes: ${attrs}.` : ""} Source: ${i.source || ""}.`;
      lines.push({
        id: `seismic_instance_${moduleName}_${key}`,
        type: "seismic_class",
        text,
        metadata: { id: key, name: i.name, class: i.class, module: moduleName },
      });
    }
  }
  return lines;
}

/* ─────────────────────────────────────────────────────────────
 * GEOMECHANICS — loaded from data/geomechanics.json and
 * data/geomechanics-fractures.json (P2.7 MEM module)
 * ───────────────────────────────────────────────────────────── */

function loadGeomechanics() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const gmPath = path.join(dataDir, "geomechanics.json");
  if (!fs.existsSync(gmPath)) return null;
  return JSON.parse(fs.readFileSync(gmPath, "utf8"));
}

function loadGeomechanicsFractures() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const gmfPath = path.join(dataDir, "geomechanics-fractures.json");
  if (!fs.existsSync(gmfPath)) return null;
  return JSON.parse(fs.readFileSync(gmfPath, "utf8"));
}

function loadFractureToGso() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const p = path.join(dataDir, "fracture_to_gso.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

/**
 * Loads the L6 corporate Petrobras geomechanics ontology
 * (data/geomechanics-corporate.json — 92 entities, 281 relations as of v1.6.2).
 * Returns null if file is absent.
 */
function loadGeomechanicsCorporate() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const p = path.join(dataDir, "geomechanics-corporate.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function loadGeomechanicsCorporateCrosswalk() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const p = path.join(dataDir, "geomechanics-corporate-crosswalk.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function buildGeomechanicsApi() {
  const gm = loadGeomechanics();
  const gmf = loadGeomechanicsFractures();
  const ftg = loadFractureToGso();
  const gmCorp = loadGeomechanicsCorporate();
  const gmCorpCw = loadGeomechanicsCorporateCrosswalk();
  if (!gm)
    return { meta: { version: VERSION, generated: NOW, error: "geomechanics.json not found" } };

  // Corporate L6 entities exposed at top level — DFIT, Breakout/Ovalização, BOL,
  // Geolog, AZIE, HAZI, etc. become directly queryable via the API endpoint.
  const corporate = gmCorp
    ? {
        meta: gmCorp.meta,
        entities: (gmCorp.entities || []).filter((e) => !e.deprecated),
        polysemy_cards: gmCorp.polysemy_cards || [],
        crosswalk_l2_l6: gmCorpCw ? { meta: gmCorpCw.meta, mappings: gmCorpCw.mappings } : null,
      }
    : null;

  return {
    meta: {
      version: VERSION,
      generated: NOW,
      source:
        "data/geomechanics.json + data/geomechanics-fractures.json + data/geomechanics-corporate.json (L6) + data/geomechanics-corporate-crosswalk.json",
      counts: {
        classes: gm.classes ? gm.classes.length : 0,
        properties: gm.properties ? gm.properties.length : 0,
        relations: gm.relations ? gm.relations.length : 0,
        instances: gm.instances ? gm.instances.length : 0,
        fracture_classes: gmf && gmf.classes ? gmf.classes.length : 0,
        fracture_to_gso_mappings: ftg && ftg.mappings ? ftg.mappings.length : 0,
        corporate_entities: corporate ? corporate.entities.length : 0,
        corporate_polysemy_cards: corporate ? corporate.polysemy_cards.length : 0,
        corporate_crosswalk_mappings:
          corporate && corporate.crosswalk_l2_l6 ? corporate.crosswalk_l2_l6.mappings.length : 0,
      },
    },
    geomechanics: gm,
    fractures: gmf,
    fracture_to_gso_crosswalk: ftg,
    corporate,
  };
}

/**
 * Converts L6 corporate entities (GEOMEC*) into entity-graph nodes.
 * Preserves label_pt as canonical; exposes acronym + observed_variants
 * as synonyms_pt; label_en as English variant. Category drives node color.
 *
 * Edges come from each entity's relationships array; only edges whose
 * target_id is another GEOMEC* node or a known graph node are emitted
 * (avoids dangling edges to entities outside the visible graph).
 *
 * F4 — Duplicate-pair merge support (option B): entities flagged
 *   `deprecated: true` + `deprecated_in_favor_of: "<surviving_id>"` are NOT
 *   emitted as their own node. Instead:
 *     1. Their outbound `relationships` are migrated onto the surviving node
 *        (source rewritten to surviving id); de-duplicated against existing
 *        edges; self-loops dropped.
 *     2. Other entities pointing AT the deprecated id have those edges
 *        retargeted to the surviving id; self-loops/dups likewise dropped.
 *     3. A `source_reference` entry is appended to the surviving node so
 *        downstream consumers preserve provenance of the merge (deprecated
 *        id, original definition, owner_department, internal_standards).
 *
 * @param {Set<string>} allowedTargetIds - IDs of non-corporate nodes that
 *   corporate edges may target (e.g. "poco" if cross-domain relations exist).
 * @returns {{nodes: Object[], edges: Object[], sourceReferences: Map<string, Object[]>, deprecationMap: Map<string, string>}}
 */
function buildGeomecCorporateGraph(allowedTargetIds) {
  const gmCorp = loadGeomechanicsCorporate();
  if (!gmCorp)
    return {
      nodes: [],
      edges: [],
      sourceReferences: new Map(),
      deprecationMap: new Map(),
    };

  const COLOR_BY_CATEGORY = {
    Process: "#0F9D9D",
    Property: "#6B5BFF",
    Tool: "#E8833A",
    Document: "#475569",
    Measurement: "#9333EA",
    Model: "#64748B",
    Formula: "#64748B",
    Risk: "#DC2626",
    Classifier: "#64748B",
    GovernanceKPI: "#15803D",
    LabTest: "#9333EA",
  };

  /* F4 deprecation map (deprecated_id -> surviving_id) for the 6 pairs merged
     in PR #33. Source schema for `deprecated`:
       - boolean true  → just filter (used by pre-existing 026B legacy field — no merge)
       - dict {replaced_by: [id], reason: str, merged_in?: str}
         · F4 merges have merged_in set (and thus generate source_reference card)
         · pre-existing splits (GEOMEC026/052/053) have replaced_by arrays without merged_in
           → still in deprecationMap so edges get rerouted, but no provenance card. */
  const deprecationMap = new Map();
  const sourceReferences = new Map();
  const survivorOf = (e) => {
    if (!e.deprecated) return null;
    if (e.deprecated === true) return null;
    const rb = e.deprecated.replaced_by;
    if (Array.isArray(rb) && rb.length > 0) return rb[0];
    return null;
  };
  for (const e of gmCorp.entities || []) {
    const survivor = survivorOf(e);
    if (survivor) deprecationMap.set(e.id, survivor);
  }

  const resolve = (id) => deprecationMap.get(id) || id;

  /* F4 — collect a provenance card for each merged corp entity so the
     surviving node carries the Petrobras-specific operational nuances.
     Only entities with `deprecated.merged_in` set (F4 merges) — pre-existing
     splits like GEOMEC026/052/053 are filtered without a provenance card. */
  for (const e of gmCorp.entities || []) {
    const survivor = survivorOf(e);
    if (!survivor) continue;
    if (!e.deprecated || typeof e.deprecated !== "object") continue;
    if (!e.deprecated.merged_in) continue;
    if (!sourceReferences.has(survivor)) sourceReferences.set(survivor, []);
    sourceReferences.get(survivor).push({
      deprecated_id: e.id,
      source_module: "data/geomechanics-corporate.json",
      label_at_merge: e.label_pt || e.label || e.id,
      label_en_at_merge: e.label_en || null,
      original_definition_pt: e.definition_pt || e.definition || null,
      original_definition_en: e.definition_en || null,
      acronym: e.acronym || [],
      observed_variants: e.observed_variants || [],
      owner_department: e.owner_department || null,
      official_datastore: e.official_datastore || null,
      internal_standards: e.internal_standards || null,
      category: e.category || null,
      sources: e.sources || [],
      merged_in: e.deprecated.merged_in,
      rationale:
        e.deprecated.reason ||
        "Conceito idêntico — " +
          survivor +
          " já cobre o termo no componente principal. Mantida proveniência Petrobras corporate.",
    });
  }

  const nodes = (gmCorp.entities || [])
    .filter((e) => !e.deprecated)
    .map((e) => {
      const synonymsPt = []
        .concat(e.label_pt_synonyms_pt || [])
        .concat(e.observed_variants || [])
        .concat(e.acronym || [])
        .filter((v, i, arr) => v && arr.indexOf(v) === i);
      const synonymsEn = e.label_en ? [e.label_en] : [];
      return {
        id: e.id,
        label: e.label_pt || e.label || e.id,
        label_en: e.label_en || null,
        type: "geomec_corporate",
        color: COLOR_BY_CATEGORY[e.category] || "#64748B",
        size: 22,
        definition: e.definition_pt || e.definition || null,
        definition_en_canonical: e.definition_en || null,
        category: e.category,
        layer: "L6",
        acronym: e.acronym || [],
        owner_department: e.owner_department || null,
        official_datastore: e.official_datastore || null,
        internal_tools: e.internal_tools || null,
        internal_standards: e.internal_standards || null,
        osdu_kind: null,
        osdu_mapping: e.osdu_mapping || null,
        geocoverage: ["layer6"],
        synonyms_pt: synonymsPt,
        synonyms_en: synonymsEn,
        examples: [],
        glossary_id: null,
        extended_id: null,
        skos_prefLabel: { "@pt": e.label_pt || e.label, "@en": e.label_en || null },
        skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
        skos_definition: {
          "@pt": e.definition_pt || e.definition || null,
          "@en": e.definition_en || null,
        },
        skos_example: [],
        wsm_type_code: e.wsm_type_code || null,
        _semantic_category: e._semantic_category || null,
      };
    });

  const corpIds = new Set(nodes.map((n) => n.id));
  /* Valid edge targets include emitted corp nodes, all non-corp graph nodes
     allowed by the caller, AND all deprecation survivor ids (which may be
     non-corp ids like "bdp" / "janela-lama" — those will be re-pointed). */
  const validTargets = new Set([
    ...corpIds,
    ...(allowedTargetIds || []),
    ...deprecationMap.values(),
  ]);

  /* Edge collection with re-routing. For each relationship:
     - Resolve source through deprecationMap (if the entity is itself
       deprecated, its outbound edges become outbound from the survivor).
     - Resolve target through deprecationMap.
     - Skip self-loops created by the rewrite (e.g. GEOMEC013 derived_from
       GEOMEC011 stays GEOMEC011-targeted, fine; but if source==target after
       rewrite, drop).
     - De-duplicate against an emitted-key set. */
  const edges = [];
  const emittedKeys = new Set();
  for (const e of gmCorp.entities || []) {
    for (const r of e.relationships || []) {
      const target = r.target_id;
      if (!target) continue;
      const newSource = resolve(e.id);
      const newTarget = resolve(target);
      if (newSource === newTarget) continue; // self-loop after merge
      if (!validTargets.has(newTarget) && !corpIds.has(newTarget)) continue;
      // Both endpoints must exist in the final graph (corp emitted OR allowed
      // OR survivor). Survivors that are non-corp must be in allowedTargetIds.
      if (!corpIds.has(newSource) && !(allowedTargetIds || new Set()).has(newSource)) {
        continue;
      }
      if (!corpIds.has(newTarget) && !(allowedTargetIds || new Set()).has(newTarget)) {
        continue;
      }
      /* Map source-side predicates to the canonical curated set
         (see docs/ONTOLOGY_PREDICATES.md §5). `related_to` is banned at
         the graph layer for being too vague — auto-promote to `references`,
         which is canonical and semantically defensible (cross-reference in
         the corporate vocab). Curator may refine specific edges to
         is_input_for / co_measured_with / preceded_by / derived_from in a
         future pass. */
      const rawRelation = (r.relation_type || "RELATED_TO").toLowerCase();
      const PREDICATE_REMAP = { related_to: "references" };
      const relation = PREDICATE_REMAP[rawRelation] || rawRelation;
      const key = `${newSource}|${newTarget}|${relation}`;
      if (emittedKeys.has(key)) continue;
      emittedKeys.add(key);
      edges.push({
        source: newSource,
        target: newTarget,
        relation,
        relation_label_pt: r.target_label || relation,
        relation_label_en: relation.replace(/_/g, " ").toLowerCase(),
        style: "geomec_corporate",
      });
    }
  }
  return { nodes, edges, sourceReferences, deprecationMap };
}

/**
 * F4 — Wires the four remaining isolated GEOMEC nodes into the main component
 * as a case-test of the 6-layer ontology model. Uses ONLY canonical predicates
 * from docs/ONTOLOGY_PREDICATES.md (no `related_to`/`used_with`).
 *
 *   GEOMEC046 Subsidência — Faixas de Risco (Classifier, L4/L5)
 *   GEOMEC076 HAZI — Azimute do Poço (Property, L1 attribute)
 *   GEOMEC086 Inversão de Slip de Falha Geológica (Process, L5 interpretation)
 *   GEOMEC087 Alinhamento de Vents Vulcânicos (Process, L4/L5 evidence)
 *
 * Each wiring traverses multiple layers (L1 well, L4 feature, L5 interpretation,
 * L6 engineering, domain anchor) so the four nodes serve as integration tests
 * for the six-layer model laid out in docs/ONTOLOGY_LAYERS.md.
 *
 * @param {Set<string>} existingIds - IDs already emitted (corp + academic +
 *   axon + main). Bridges only fire when both endpoints exist.
 * @returns {{nodes: Object[], edges: Object[]}}
 */
function buildIsolatedGeomecBridges(existingIds) {
  const edges = [];
  const seen = new Set();
  const add = (source, target, relation, labelPt, labelEn) => {
    if (!existingIds.has(source) || !existingIds.has(target)) return;
    if (source === target) return;
    const k = `${source}|${target}|${relation}`;
    if (seen.has(k)) return;
    seen.add(k);
    edges.push({
      source,
      target,
      relation,
      relation_label_pt: labelPt || relation.replace(/_/g, " "),
      relation_label_en: labelEn || relation.replace(/_/g, " "),
      style: "geomec_isolated_bridge",
    });
  };

  /* GEOMEC046 — Subsidência — Faixas de Risco (Classifier).
     L4/L5: classifier produced by IMGR (GEOMEC027), specializes Subsidência
     (GEOMEC016), grounded on academic MEM 1D (GM010-12) and the Geomecânica
     domain anchor. */
  add(
    "GEOMEC046",
    "GEOMEC016",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  add("GEOMEC027", "GEOMEC046", "produces", "produz", "produces");
  add("GEOMEC046", "axon-dom-geomecanica", "is_part_of", "é parte de", "is part of");
  add("GEOMEC046", "reservatorio", "applies_to", "aplica-se a", "applies to");
  add("GEOMEC046", "GM010", "derived_from", "derivado de", "derived from");
  add("GEOMEC046", "GM011", "derived_from", "derivado de", "derived from");
  add("GEOMEC046", "GM012", "derived_from", "derivado de", "derived from");
  /* Risk classifier supports stability assessment (GEOMEC015 Estab. Poço). */
  add("GEOMEC046", "GEOMEC015", "supports", "apoia", "supports");

  /* GEOMEC076 — HAZI — Azimute do Poço (well attribute concept).
     Per ONTOLOGY_LAYERS §5: well_attribute_concept attached to L1 Well via
     applies_to. Used as input to image-log interpretation (GEOMEC023, 072)
     and co-measured with AZIE (GEOMEC075). */
  add("GEOMEC076", "poco", "applies_to", "aplica-se a", "applies to");
  add("GEOMEC076", "GEOMEC023", "is_input_for", "é entrada para", "is input for");
  add("GEOMEC076", "GEOMEC072", "is_input_for", "é entrada para", "is input for");
  add("GEOMEC076", "axon-dom-geomecanica", "is_part_of", "é parte de", "is part of");
  add("GEOMEC076", "GEOMEC075", "co_measured_with", "co-medido com", "co-measured with");

  /* GEOMEC086 — Inversão de Slip de Falha Geológica (Process, L5).
     Interpretation process producing principal stress axes (GEOMEC081),
     observed on faults (falha), specialization of well-evaluation processes,
     formalized by GEOMEC083 (Inversão Formal de Mecanismos Focais). */
  add("GEOMEC086", "GEOMEC081", "produces", "produz", "produces");
  add("GEOMEC086", "falha", "observed_in", "observado em", "observed in");
  add("GEOMEC086", "GEOMEC082", "derived_from", "derivado de", "derived from");
  add("GEOMEC083", "GEOMEC086", "formalizes", "formaliza", "formalizes");
  add("GEOMEC086", "axon-dom-geomecanica", "is_part_of", "é parte de", "is part of");
  add("GEOMEC086", "GEOMEC017", "supports", "apoia", "supports");
  add(
    "GEOMEC086",
    "axon-asn-aval-final-poco",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );

  /* GEOMEC087 — Alinhamento de Vents Vulcânicos (Process / WSM 2025 indicator).
     Stress-orientation indicator: input to principal stress axes (GEOMEC081),
     derived from WSM 2025 quality scheme (GEOMEC084), co-measured with focal
     mechanisms (GEOMEC082). */
  add("GEOMEC087", "GEOMEC081", "is_input_for", "é entrada para", "is input for");
  add("GEOMEC087", "GEOMEC084", "derived_from", "derivado de", "derived from");
  add("GEOMEC087", "axon-dom-geomecanica", "is_part_of", "é parte de", "is part of");
  add("GEOMEC087", "GEOMEC082", "co_measured_with", "co-medido com", "co-measured with");

  return { nodes: [], edges };
}

/**
 * Converts the L1-L2 academic backbone of geomechanics — 27 GM* classes from
 * data/geomechanics.json (Fjaer/Zoback/ISRM) and 17 GF* fracture classes from
 * data/geomechanics-fractures.json (Pillar 4 / structural geology) — into
 * entity-graph nodes plus a dense set of edges:
 *   1. Internal (within-cluster) edges from each source's `relations` array
 *      and from `superclass` taxonomy where the parent is also an emitted node.
 *   2. Bridge edges from academic GM* / GF* classes to existing main-component
 *      pivots (poco, wireline-logging, formation-testing, core-sample,
 *      janela-lama, campo-tensional, ...) so the new sub-cluster merges into
 *      the giant main component.
 *   3. Bridge edges from existing L6 corporate GEOMEC* nodes to their
 *      academic GM* / GF* counterparts via `is_specialization_of` /
 *      `derived_from`, so the L6 island merges through the academic layer.
 *
 * Vocabulary uses only the curated predicate set (no invented terms):
 *   is_specialization_of, derived_from, produces, is_part_of,
 *   is_calculated_from, is_input_for, measures, monitors, governed_by,
 *   requires, constrains, formalizes, calibrates, supports, enables,
 *   co_measured_with, estimates, requires_input, computes,
 *   acquired_from, interpreted_into, observed_in, applies_to, occurs_in.
 *
 * @param {Set<string>} existingIds - Set of node IDs already emitted by
 *   buildEntityGraph (main component + L6 island + isolated). Used to gate
 *   bridge edges so we never author dangling edges.
 * @returns {{nodes: Object[], edges: Object[]}}
 */
function buildGeomecAcademicGraph(existingIds) {
  const gm = loadGeomechanics();
  const gmf = loadGeomechanicsFractures();
  if (!gm && !gmf) return { nodes: [], edges: [] };

  const COLOR_ACADEMIC = "#8B4789"; // purple — distinct from geomec_corporate palette
  const COLOR_FRACTURE = "#B85A3E"; // terracotta — distinct from existing colors

  /**
   * Builds an entity-graph node from a GM* / GF* class object.
   */
  const mkNode = (cls, kind) => {
    const isFracture = kind === "geomec_fracture";
    const labelPt = cls.name_pt || cls.name;
    const labelEn = cls.name;
    const definitionPt = cls.description_pt || cls.description || null;
    const definitionEn = cls.description || null;
    const synonymsPt = [];
    const synonymsEn = [];
    const baseGeocoverage = isFracture ? ["layer1", "layer2", "layer7"] : ["layer1", "layer2"];
    const examples = [];
    return {
      id: cls.id,
      label: labelPt,
      label_en: labelEn,
      type: kind,
      color: isFracture ? COLOR_FRACTURE : COLOR_ACADEMIC,
      size: 22,
      definition: definitionPt,
      definition_en_canonical: definitionEn,
      legal_source: Array.isArray(cls.sources) ? cls.sources.join("; ") : null,
      datasets: [],
      petrokgraph_uri: null,
      osdu_kind: null,
      /* Fix: gso_uri (Layer 7) is NOT a GeoSciML URI (Layer 1b). The
         entity-graph linter requires geosciml_uri to start with
         http://geosciml.org/. Keep them in distinct fields. */
      geosciml_uri: cls.geosciml_uri || null,
      owl_uri: null,
      geocoverage:
        cls.geocoverage && cls.geocoverage.length
          ? cls.geocoverage.filter((g) => g !== "sweet" && g !== "layer6")
          : baseGeocoverage,
      synonyms_pt: synonymsPt,
      synonyms_en: synonymsEn,
      examples,
      glossary_id: null,
      extended_id: null,
      sweet_alignment: cls.sweet_alignment || cls.sweet_uri || null,
      gso_uri: cls.gso_uri || null,
      superclass: cls.superclass || null,
      layer: isFracture ? "L1-L2-L7" : "L1-L2",
      skos_prefLabel: { "@pt": labelPt, "@en": labelEn },
      skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
      skos_definition: { "@pt": definitionPt, "@en": definitionEn },
      skos_example: examples,
    };
  };

  const nodes = [];
  for (const cls of (gm && gm.classes) || []) nodes.push(mkNode(cls, "geomec_academic"));
  for (const cls of (gmf && gmf.classes) || []) nodes.push(mkNode(cls, "geomec_fracture"));

  const academicIds = new Set(nodes.map((n) => n.id));

  /* Build a name -> id index for relations (relations reference class names,
     not IDs, e.g. domain "StressTensor" maps to GM001). */
  const nameToId = new Map();
  for (const cls of (gm && gm.classes) || []) {
    nameToId.set(cls.name, cls.id);
    if (cls.name_pt) nameToId.set(cls.name_pt, cls.id);
  }
  for (const cls of (gmf && gmf.classes) || []) {
    nameToId.set(cls.name, cls.id);
    if (cls.name_pt) nameToId.set(cls.name_pt, cls.id);
  }

  const edges = [];
  const seen = new Set(); // de-dup key
  const addEdge = (source, target, relation, labelPt, labelEn, style) => {
    if (!source || !target || source === target) return;
    const key = `${source} ${target} ${relation}`;
    if (seen.has(key)) return;
    seen.add(key);
    edges.push({
      source,
      target,
      relation,
      relation_label_pt: labelPt || relation.replace(/_/g, " "),
      relation_label_en: labelEn || relation.replace(/_/g, " "),
      style: style || "geomec_academic",
    });
  };

  /* ─── 1. Internal edges from `relations` (GR* in geomechanics.json) ─── */
  const relList = [...((gm && gm.relations) || []), ...((gmf && gmf.relations) || [])];
  for (const r of relList) {
    const src = nameToId.get(r.domain);
    const tgt = nameToId.get(r.range);
    if (!src || !tgt) continue;
    if (!academicIds.has(src) || !academicIds.has(tgt)) continue;
    addEdge(src, tgt, r.name, r.name_pt || r.name, r.name);
  }

  /* ─── 1b. Internal edges from `superclass` taxonomy.
     When a class's superclass matches another emitted class's name, emit an
     `is_specialization_of` edge from the subclass to the parent. ─── */
  for (const cls of [...((gm && gm.classes) || []), ...((gmf && gmf.classes) || [])]) {
    const parentId = nameToId.get(cls.superclass);
    if (!parentId || parentId === cls.id) continue;
    if (!academicIds.has(parentId)) continue;
    addEdge(
      cls.id,
      parentId,
      "is_specialization_of",
      "é especialização de",
      "is specialization of"
    );
  }

  /* ─── 2. Bridge edges from academic to MAIN component ─── */
  // helper that only emits if the target exists in the existing graph
  const bridgeMain = (src, tgt, rel, labelPt, labelEn) => {
    if (!existingIds.has(tgt)) return;
    if (!academicIds.has(src)) return;
    addEdge(src, tgt, rel, labelPt, labelEn, "geomec_academic_bridge");
  };

  // Pore pressure & stress measurements — formation-testing measures pore pressure
  bridgeMain("GM004", "formation-testing", "measures", "é medido por", "is measured by");
  bridgeMain("GM004", "wireline-logging", "derived_from", "derivado de", "derived from");
  bridgeMain("GM001", "formation-testing", "measures", "é medido por", "is measured by");
  bridgeMain("GM002", "formation-testing", "measures", "é medido por", "is measured by");
  bridgeMain("GM003", "formation-testing", "measures", "é medido por", "is measured by");

  // MEM family — derived from logs/cores/tests, produces janela-lama and campo-tensional
  for (const memId of ["GM010", "GM011", "GM012"]) {
    bridgeMain(memId, "wireline-logging", "derived_from", "derivado de", "derived from");
    bridgeMain(memId, "core-sample", "derived_from", "derivado de", "derived from");
    bridgeMain(memId, "formation-testing", "derived_from", "derivado de", "derived from");
    bridgeMain(memId, "janela-lama", "produces", "produz", "produces");
    bridgeMain(memId, "campo-tensional", "produces", "produz", "produces");
  }

  // Wellbore (GM026) — academic specialization of operational poco
  bridgeMain(
    "GM026",
    "poco",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  // MudWindow academic specialization of analytical janela-lama
  bridgeMain(
    "GM005",
    "janela-lama",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  // AndersonStressRegime academic specialization of analytical campo-tensional
  bridgeMain(
    "GM025",
    "campo-tensional",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );

  // Rock mech properties (UCS, Young, Poisson, Biot, Bulk, Shear) derived from core-sample/wireline
  for (const propId of ["GM013", "GM014", "GM015", "GM016", "GM017", "GM018", "GM019"]) {
    bridgeMain(propId, "core-sample", "derived_from", "derivado de", "derived from");
    bridgeMain(propId, "wireline-logging", "derived_from", "derivado de", "derived from");
  }

  // RQD/GSI/RMR — estimated from core descriptions (cuttings as fallback)
  for (const cls of ["GM020", "GM021", "GM022"]) {
    bridgeMain(cls, "core-sample", "derived_from", "derivado de", "derived from");
  }

  // Wellbore observations — log-based (mwd-lwd, lwd, mwd) calibrate MEM
  bridgeMain("GM010", "mwd-lwd", "calibrates", "calibra", "calibrates");
  bridgeMain("GM010", "lwd", "calibrates", "calibra", "calibrates");
  bridgeMain("GM010", "mwd", "calibrates", "calibra", "calibrates");

  // BDP (banco de dados de poços) — observed_in records of MEM/Pp/regime
  bridgeMain("GM010", "bdp", "observed_in", "observado em", "observed in");

  // Fracture classes — derived from core, image logs (wireline), cuttings
  for (const fid of [
    "GF004",
    "GF005",
    "GF006",
    "GF007",
    "GF008",
    "GF009",
    "GF010",
    "GF011",
    "GF015",
    "GF016",
    "GF017",
  ]) {
    bridgeMain(fid, "wireline-logging", "derived_from", "derivado de", "derived from");
    bridgeMain(fid, "core-sample", "derived_from", "derivado de", "derived from");
  }

  // Laudo Geomecânico already exists in main as a doc — academic GM027 specializes it
  bridgeMain("GM027", "laudo-geomecanico", "formalizes", "formaliza", "formalizes");

  // MohrCircle (GM006) — método gráfico que representa a transformação do estado
  // de tensões/deformações em um ponto quando muda a orientação do plano analisado;
  // permite determinar tensões principais, tensão de cisalhamento máxima e a
  // orientação dos planos onde essas grandezas ocorrem. Usado em análise de
  // mecanismo de deformação (em especial via critério Mohr-Coulomb para falha frágil).
  if (academicIds.has("GM006") && academicIds.has("GM001")) {
    addEdge("GM006", "GM001", "is_calculated_from", "calculado a partir de", "is calculated from");
  }
  if (academicIds.has("GM006") && academicIds.has("GM007")) {
    addEdge("GM006", "GM007", "supports", "apoia", "supports");
  }
  if (academicIds.has("GM006") && academicIds.has("GF001")) {
    addEdge("GM006", "GF001", "is_input_for", "é entrada para", "is input for");
  }
  if (academicIds.has("GM006") && academicIds.has("GF002")) {
    addEdge("GM006", "GF002", "supports", "apoia", "supports");
  }

  // DeformationMechanism family (GF001, GF002, GF003) — connect to academic
  // brittle/ductile parents and to FractureType so the trio joins the cluster.
  if (academicIds.has("GF002") && academicIds.has("GF001")) {
    addEdge(
      "GF002",
      "GF001",
      "is_specialization_of",
      "é especialização de",
      "is specialization of"
    );
  }
  if (academicIds.has("GF003") && academicIds.has("GF001")) {
    addEdge(
      "GF003",
      "GF001",
      "is_specialization_of",
      "é especialização de",
      "is specialization of"
    );
  }
  // Brittle deformation produces fractures (FractureType) — tie GF002 to GF004
  if (academicIds.has("GF002") && academicIds.has("GF004")) {
    addEdge("GF002", "GF004", "produces", "produz", "produces");
  }
  // Brittle deformation occurs in wellbore — bridge to operational pivot
  bridgeMain("GF002", "poco", "occurs_in", "ocorre em", "occurs in");
  // Deformation in general — observed in core
  bridgeMain("GF001", "core-sample", "observed_in", "observado em", "observed in");
  bridgeMain("GF003", "core-sample", "observed_in", "observado em", "observed in");

  /* ─── 3. Bridge edges from existing L6 corporate to academic ─── */
  const bridgeCorp = (corpId, acadId, rel, labelPt, labelEn) => {
    if (!existingIds.has(corpId)) return;
    if (!academicIds.has(acadId)) return;
    addEdge(corpId, acadId, rel, labelPt, labelEn, "geomec_corp_to_academic");
  };

  // Pp / stresses
  bridgeCorp(
    "GEOMEC001",
    "GM004",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC002",
    "GM002",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC003",
    "GM005",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC004",
    "GM001",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC007",
    "GM002",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC008",
    "GM002",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );

  // Rock mech properties — UCS, E, nu, Biot
  bridgeCorp(
    "GEOMEC010",
    "GM014",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC011",
    "GM015",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC012",
    "GM016",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC013",
    "GM017",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );

  // Stress regime
  bridgeCorp(
    "GEOMEC017",
    "GM025",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );

  // Fracture/breakout observations — corporate (image-log derived) → academic
  // GEOMEC068 Ovalização (breakout) is a wellbore measurement — derived from drilling
  // GEOMEC069 Drilling-induced fracture — kinematic class is Joint (Mode I, tensile)
  // GEOMEC070 Natural fracture — academic FractureType
  // GEOMEC023A/B/C are processes that produce these features
  bridgeCorp("GEOMEC068", "GM026", "observed_in", "observado em", "observed in");
  bridgeCorp(
    "GEOMEC069",
    "GF005",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp(
    "GEOMEC070",
    "GF004",
    "is_specialization_of",
    "é especialização de",
    "is specialization of"
  );
  bridgeCorp("GEOMEC023A", "GM026", "occurs_in", "ocorre em", "occurs in");
  bridgeCorp("GEOMEC023B", "GF005", "produces", "produz", "produces");
  bridgeCorp("GEOMEC023C", "GF004", "interpreted_into", "interpretado em", "interpreted into");

  return { nodes, edges };
}

/* ─────────────────────────────────────────────────────────────
 * AXON PETROBRAS — loaded from data/axon-petrobras-glossary.json (F3)
 * ───────────────────────────────────────────────────────────── */

function loadAxonPetrobrasGlossary() {
  const dataDir = path.resolve(__dirname, "..", "data");
  const p = path.join(dataDir, "axon-petrobras-glossary.json");
  if (!fs.existsSync(p)) return null;
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

/**
 * Builds the Axon Petrobras (Exploração) hierarchy as a sub-graph and bridges
 * it into the existing entity-graph by anchoring Axon Domínio super-topics on
 * existing operational, analytical, contractual, geological and
 * `geomec_corporate`/`geomec_academic`/`geomec_fracture` pivots.
 *
 * Hierarchy emitted as nodes:
 *   - Domínios (9) → new type `axon_domain`, color #D4A017 (golden), L6 corporate.
 *   - Assuntos and Subassuntos → reuse existing `analytical` type (visual harmony
 *     with operations like wireline-logging) so the sub-graph blends visually.
 *   - Termo "amostra" → reuse `analytical` type (sample artifact).
 *   - Termo "furo" → reuse `analytical` type (sibling investigation tool to poco).
 *   - Termo "sonda" → reuse `equipment` type.
 *   - Lâmina d'água + 3 sub-classes (rasa, profunda, ultraprofunda) → `analytical`.
 *   - Poço subtypes (comprado, pré-sal, não BR) → `analytical`.
 *   - Ambiente sub-vocab (mar, terra, lago) → `geological` (matches `ambiente`).
 *
 * Bridges:
 *   - Each operação geológica (wireline-logging, mudlogging, coring, ...)
 *     `is_specialization_of` the matching Axon Assunto.
 *   - Each amostra (core-sample, fluid-sample, ...) `is_specialization_of`
 *     `axon-term-amostra`.
 *   - Existing `igp` → `is_part_of` `axon-dom-geologia` and Domínio
 *     `Avaliação final de poço` Assunto.
 *   - Existing `campo` → `is_part_of` `axon-dom-blocos-parcerias`.
 *   - Geomec dom: 5–8 representative geomec nodes (corporate, academic,
 *     fracture) `is_part_of` `axon-dom-geomecanica`.
 *   - Lâmina d'água sub-classes `is_specialization_of` `axon-term-lamina-agua`.
 *   - Poço subtypes `is_specialization_of` `poco`.
 *
 * Vocabulary used (all from docs/ONTOLOGY_PREDICATES.md, no invented terms):
 *   is_part_of, is_specialization_of, performed_by, applies_to, supports,
 *   governed_by, requires, observed_in, occurs_in.
 *
 * @param {Set<string>} existingIds - Set of node IDs already emitted by
 *   buildEntityGraph (main component + L6 corporate island + L1-L2 academic
 *   sub-graph + isolated). Used to gate bridge edges so we never author
 *   dangling edges.
 * @returns {{nodes: Object[], edges: Object[]}}
 */
function buildAxonGlossaryGraph(existingIds) {
  const axon = loadAxonPetrobrasGlossary();
  if (!axon) return { nodes: [], edges: [] };

  const COLOR_AXON_DOMAIN = "#D4A017"; // golden — Axon Domínio super-topics
  const COLOR_ANALYTICAL = "#E67E22"; // reuse analytical palette
  const COLOR_EQUIPMENT = "#C77B30"; // reuse equipment palette
  const COLOR_GEOLOGICAL = "#639922"; // reuse geological palette

  const nodes = [];
  const seen = new Set();
  const seenEdgeKey = new Set();

  /* Helper to mint a node with the entity-graph schema. */
  const mkNode = (entry, type, color, geocoverage, sizeHint) => {
    const labelPt = entry.name_pt;
    const labelEn = entry.name_en || entry.name_pt;
    const definitionPt = entry.definition_pt_canonical || entry.definition_pt || null;
    const synonymsPt = Array.isArray(entry.synonyms_pt) ? entry.synonyms_pt : [];
    const synonymsEn = Array.isArray(entry.synonyms_en) ? entry.synonyms_en : [];
    return {
      id: entry.id,
      label: labelPt,
      label_en: labelEn,
      type,
      color,
      size: sizeHint || 22,
      definition: definitionPt,
      definition_en_canonical: null,
      legal_source: entry.legal_source || null,
      datasets: [],
      petrokgraph_uri: null,
      osdu_kind: null,
      geosciml_uri: null,
      owl_uri: null,
      geocoverage,
      synonyms_pt: synonymsPt,
      synonyms_en: synonymsEn,
      examples: [],
      glossary_id: null,
      extended_id: null,
      axon_type: entry.axon_type,
      axon_path: entry.axon_path || null,
      skos_prefLabel: { "@pt": labelPt, "@en": labelEn },
      skos_altLabel: { "@pt": synonymsPt, "@en": synonymsEn },
      skos_definition: { "@pt": definitionPt, "@en": null },
      skos_example: [],
    };
  };

  const addNode = (n) => {
    if (seen.has(n.id)) return;
    if (existingIds.has(n.id)) return; // never duplicate an existing graph node
    seen.add(n.id);
    nodes.push(n);
  };

  /* 1. Area — emit as the Axon root. Then 9 Domínios. */
  for (const area of axon.areas || []) {
    addNode(mkNode(area, "axon_domain", COLOR_AXON_DOMAIN, ["layer6"], 30));
  }
  for (const dom of axon.domains || []) {
    addNode(mkNode(dom, "axon_domain", COLOR_AXON_DOMAIN, ["layer6"], 26));
  }

  /* 2. Subjects (Assuntos) — analytical, layer6 (Petrobras corporate), with
     occasional layer4 (OSDU) when there is a clear OSDU pivot via existing
     operations they specialize. */
  for (const sub of axon.subjects || []) {
    addNode(mkNode(sub, "analytical", COLOR_ANALYTICAL, ["layer6"], 22));
  }

  /* 3. Subsubjects (Subassuntos) — analytical, layer6. */
  for (const ss of axon.subsubjects || []) {
    addNode(mkNode(ss, "analytical", COLOR_ANALYTICAL, ["layer6"], 20));
  }

  /* 4. Termos — emit only the ones that are NOT format-only attributes (those
     live in data/well-attributes.json). The terms array in the source already
     excludes the format-only set; here we still classify by id. */
  const TERM_TYPE = {
    "axon-term-acervo-amostras": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer6"],
      size: 22,
    },
    "axon-term-amostra": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer1", "layer2", "layer4", "layer6"],
      size: 24,
    },
    "axon-term-amostragem-calha-prevista": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer6"],
      size: 20,
    },
    "axon-term-ambiente": {
      type: "geological",
      color: COLOR_GEOLOGICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 20,
    },
    "axon-term-campo": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 20,
    },
    "axon-term-classificacao-poco": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 20,
    },
    "axon-term-furo": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer1", "layer4", "layer5", "layer6"],
      size: 22,
    },
    "axon-term-igp": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 20,
    },
    "axon-term-lamina-agua": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 22,
    },
    "axon-term-lamina-agua-rasa": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 18,
    },
    "axon-term-lamina-agua-profunda": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 18,
    },
    "axon-term-lamina-agua-ultraprofunda": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 18,
    },
    "axon-term-objetivo-poco": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 18,
    },
    "axon-term-poco": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer4", "layer5", "layer6"],
      size: 20,
    },
    "axon-term-poco-comprado": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 20,
    },
    "axon-term-poco-presal": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 20,
    },
    "axon-term-poco-nao-br": {
      type: "analytical",
      color: COLOR_ANALYTICAL,
      geo: ["layer5", "layer6"],
      size: 20,
    },
    "axon-term-sonda": {
      type: "equipment",
      color: COLOR_EQUIPMENT,
      geo: ["layer4", "layer5", "layer6"],
      size: 22,
    },
  };

  for (const term of axon.terms || []) {
    const cfg = TERM_TYPE[term.id];
    if (!cfg) continue; // any term we explicitly chose not to materialize
    // Skip terms that refer to an existing graph id (e.g., "igp", "campo")
    // — we'll bridge to those instead of duplicating. The Axon term node we
    // emit is always axon-prefixed; it's an *additional* concept node tied to
    // the Petrobras hierarchy, not a duplicate of the existing pivot.
    if (existingIds.has(term.id)) continue;
    addNode(mkNode(term, cfg.type, cfg.color, cfg.geo, cfg.size));
  }

  const axonIds = new Set(nodes.map((n) => n.id));

  const addEdge = (source, target, relation, labelPt, labelEn, style) => {
    if (!source || !target || source === target) return;
    if (!axonIds.has(source) && !existingIds.has(source)) return;
    if (!axonIds.has(target) && !existingIds.has(target)) return;
    const key = `${source} ${target} ${relation}`;
    if (seenEdgeKey.has(key)) return;
    seenEdgeKey.add(key);
    edges.push({
      source,
      target,
      relation,
      relation_label_pt: labelPt || relation.replace(/_/g, " "),
      relation_label_en: labelEn || relation.replace(/_/g, " "),
      style: style || "axon_internal",
    });
  };

  const edges = [];

  /* ─── A. Internal hierarchy edges from parent_id ─── */
  const allEntries = [
    ...(axon.areas || []),
    ...(axon.domains || []),
    ...(axon.subjects || []),
    ...(axon.subsubjects || []),
    ...(axon.terms || []),
  ];
  for (const e of allEntries) {
    if (!e.parent_id) continue;
    if (!axonIds.has(e.id)) continue; // not emitted (e.g., format-only term)
    if (!axonIds.has(e.parent_id) && !existingIds.has(e.parent_id)) continue;
    addEdge(e.id, e.parent_id, "is_part_of", "faz parte de", "is part of", "axon_hierarchy");
  }

  /* ─── B. Existing operations specialize Axon Assuntos ─── */
  const specBridge = (childId, parentId) => {
    if (!existingIds.has(childId)) return;
    if (!axonIds.has(parentId)) return;
    addEdge(
      childId,
      parentId,
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_op_bridge"
    );
  };

  // Operação de Perfilagem
  specBridge("wireline-logging", "axon-asn-perfilagem");
  specBridge("wireline-run", "axon-asn-perfilagem");
  specBridge("mwd-lwd", "axon-asn-perfilagem");
  specBridge("lwd-run", "axon-asn-perfilagem");

  // Operação de Testemunhagem
  specBridge("coring", "axon-asn-testemunhagem");
  specBridge("core-run", "axon-asn-testemunhagem");
  specBridge("sidewall-sampling", "axon-asn-testemunhagem");

  // Operações de Mudlogging
  specBridge("mudlogging", "axon-asn-mudlogging");
  specBridge("mudlogging-time-series", "axon-asn-mudlogging");
  specBridge("cuttings-sampling", "axon-asn-mudlogging");
  specBridge("cuttings-sample-detailed", "axon-asn-mudlogging");

  // Teste de formação a poço aberto
  specBridge("formation-testing", "axon-asn-teste-formacao-aberto");
  specBridge("teste-formacao", "axon-asn-teste-formacao-aberto");
  // dst-interval is part of (not specialization) — it's an interval scoped to
  // the test, not a sub-kind of the operation
  if (existingIds.has("dst-interval") && axonIds.has("axon-asn-teste-formacao-aberto")) {
    addEdge(
      "dst-interval",
      "axon-asn-teste-formacao-aberto",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_op_bridge"
    );
  }

  // Registro de pressão de formação e temperatura
  specBridge("rftp", "axon-asn-pressao-temperatura");

  /* ─── C. Sample artifacts specialize generic axon-term-amostra ─── */
  const sampleSpec = (childId) => {
    if (!existingIds.has(childId)) return;
    if (!axonIds.has("axon-term-amostra")) return;
    addEdge(
      childId,
      "axon-term-amostra",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_sample_bridge"
    );
  };
  sampleSpec("core-sample");
  sampleSpec("core-plug");
  sampleSpec("sidewall-core-sample");
  sampleSpec("cuttings-sample-detailed");
  sampleSpec("fluid-sample");
  sampleSpec("amostra-fluido");
  sampleSpec("testemunho");

  /* ─── D. Acervo de amostras anchors the sample collection ─── */
  if (existingIds.has("axon-term-acervo-amostras")) {
    // already in axonIds
  }
  // axon-term-amostra is_part_of acervo (mereologically a sample is part of the collection)
  addEdge(
    "axon-term-amostra",
    "axon-term-acervo-amostras",
    "is_part_of",
    "faz parte de",
    "is part of",
    "axon_internal"
  );
  // Acervo is anchored on its Domínio
  addEdge(
    "axon-term-acervo-amostras",
    "axon-dom-acervo-amostras",
    "is_part_of",
    "faz parte de",
    "is part of",
    "axon_hierarchy"
  );

  /* ─── E. Furo handling: NOT a specialization of poco. Furo is an
     investigation tool sibling — sits inside Domínio Geologia, not under
     poco. ─── */
  addEdge(
    "axon-term-furo",
    "axon-dom-geologia",
    "is_part_of",
    "faz parte de",
    "is part of",
    "axon_dom_link"
  );
  // It also conceptually relates to the Axon Subassunto "Dados culturais de poços e sonda"
  // via the source hierarchy edge (parent_id), already emitted in §A.

  /* ─── F. Sonda — predicate direction: drilling-activity performed_by sonda.
     This is the canonical L2 → equipment direction.
     Also: sonda is_part_of Domínio Geologia (sonda is a technical tool inside
     the data acquisition apparatus). ─── */
  if (existingIds.has("drilling-activity") && axonIds.has("axon-term-sonda")) {
    addEdge(
      "drilling-activity",
      "axon-term-sonda",
      "performed_by",
      "executado por",
      "performed by",
      "axon_op_to_equipment"
    );
  }
  // Wireline-logging, mudlogging, coring, formation-testing also performed_by sonda
  for (const op of [
    "wireline-logging",
    "mudlogging",
    "coring",
    "formation-testing",
    "wireline-run",
    "core-run",
  ]) {
    if (existingIds.has(op) && axonIds.has("axon-term-sonda")) {
      addEdge(
        op,
        "axon-term-sonda",
        "performed_by",
        "executado por",
        "performed by",
        "axon_op_to_equipment"
      );
    }
  }
  // Sonda anchored on Aquisição de dados geológicos (it executes those operations)
  addEdge(
    "axon-term-sonda",
    "axon-dom-aquisicao-dados-geo",
    "supports",
    "apoia",
    "supports",
    "axon_dom_link"
  );

  /* ─── G. Domínio Aquisição: anchor 4 main Assuntos under it (already done
     by §A via parent_id). No extra edges needed. ─── */

  /* ─── H. Domínio Acervo de amostras: anchor amostra (§D done). ─── */

  /* ─── I. Domínio Geomecânica: pick representative nodes from corporate,
     academic and fracture clusters. Not all 130+ — only key anchors. ─── */
  const geomecAnchors = [
    "GEOMEC001", // Pressão de Poros
    "GEOMEC004", // Geotensões
    "GEOMEC025", // CSD
    "GEOMEC084", // Esquema de Qualidade WSM 2025
    "GM010", // ModeloMecanicoTerra (MEM)
    "GM025", // AndersonStressRegime
    "GF001", // MecanismoDeDeformacao
    "GF004", // TipoDeFratura
    "ogeomec", // Ocorrências Geomecânicas
    "laudo-geomecanico", // Laudo Geomecânico
  ];
  for (const id of geomecAnchors) {
    if (existingIds.has(id) && axonIds.has("axon-dom-geomecanica")) {
      addEdge(
        id,
        "axon-dom-geomecanica",
        "is_part_of",
        "faz parte de",
        "is part of",
        "axon_geomec_anchor"
      );
    }
  }

  /* ─── J. IGP: enrich, do not duplicate. The Axon hierarchy puts IGP under
     "Dados culturais de poços e sonda" (Subassunto), but semantically IGP is
     also a deliverable of the geological data acquisition program. We bridge
     the existing `igp` node via is_part_of to the Domínio Geologia (for
     organization) and Aquisição de dados geológicos. ─── */
  if (existingIds.has("igp") && axonIds.has("axon-dom-aquisicao-dados-geo")) {
    addEdge(
      "igp",
      "axon-dom-aquisicao-dados-geo",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_dom_link"
    );
  }
  if (existingIds.has("igp") && axonIds.has("axon-asn-aval-final-poco")) {
    addEdge("igp", "axon-asn-aval-final-poco", "supports", "apoia", "supports", "axon_op_bridge");
  }
  if (existingIds.has("igp") && axonIds.has("axon-term-igp")) {
    // axon-term-igp formaliza o IGP existente: identidade conceitual via
    // is_specialization_of (axon-term-igp é a definição Axon do mesmo objeto
    // de negócio modelado no nó `igp`).
    addEdge(
      "axon-term-igp",
      "igp",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_term_to_existing"
    );
  }

  /* ─── K. Campo: enrich, do not duplicate. Existing `campo` node bridges to
     Blocos e Parcerias (Domínio) and the Axon term node `axon-term-campo`
     specializes it. ─── */
  if (existingIds.has("campo") && axonIds.has("axon-dom-blocos-parcerias")) {
    addEdge(
      "campo",
      "axon-dom-blocos-parcerias",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_dom_link"
    );
  }
  if (existingIds.has("campo") && axonIds.has("axon-term-campo")) {
    addEdge(
      "axon-term-campo",
      "campo",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_term_to_existing"
    );
  }

  /* ─── L. Lâmina d'água sub-classes specialize the parent Axon term ─── */
  for (const sub of [
    "axon-term-lamina-agua-rasa",
    "axon-term-lamina-agua-profunda",
    "axon-term-lamina-agua-ultraprofunda",
  ]) {
    if (axonIds.has(sub) && axonIds.has("axon-term-lamina-agua")) {
      addEdge(
        sub,
        "axon-term-lamina-agua",
        "is_specialization_of",
        "é especialização de",
        "is specialization of",
        "axon_internal"
      );
    }
  }
  // Lâmina d'água applies to poco
  if (axonIds.has("axon-term-lamina-agua") && existingIds.has("poco")) {
    addEdge(
      "axon-term-lamina-agua",
      "poco",
      "applies_to",
      "aplica-se a",
      "applies to",
      "axon_attr_bridge"
    );
  }

  /* ─── M. Poço subtypes specialize existing `poco` ─── */
  for (const sub of ["axon-term-poco-comprado", "axon-term-poco-presal", "axon-term-poco-nao-br"]) {
    if (axonIds.has(sub) && existingIds.has("poco")) {
      addEdge(
        sub,
        "poco",
        "is_specialization_of",
        "é especialização de",
        "is specialization of",
        "axon_poco_subtype"
      );
    }
  }
  // Existing presal already exists — pre-sal well is a specialization that references it
  if (axonIds.has("axon-term-poco-presal") && existingIds.has("presal")) {
    addEdge(
      "axon-term-poco-presal",
      "presal",
      "occurs_in",
      "ocorre em",
      "occurs in",
      "axon_term_to_existing"
    );
  }
  // axon-term-poco itself is_specialization_of the existing poco (the Axon
  // definition formalizes the same business concept)
  if (axonIds.has("axon-term-poco") && existingIds.has("poco")) {
    addEdge(
      "axon-term-poco",
      "poco",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_term_to_existing"
    );
  }

  /* ─── N. Ambiente: existing `ambiente` is the controlled-vocab anchor. The
     Axon term axon-term-ambiente specializes it. ─── */
  if (axonIds.has("axon-term-ambiente") && existingIds.has("ambiente")) {
    addEdge(
      "axon-term-ambiente",
      "ambiente",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_term_to_existing"
    );
  }

  /* ─── O. Classificação do poço: link to ANP categoria-1..10 anchor.
     The vocabulary lives in data/anp-poco-categoria.json — there is a parent
     concept node `anp-poco-categoria` if loaded. We bridge by attempting both
     the parent concept and the specific values. ─── */
  if (axonIds.has("axon-term-classificacao-poco") && existingIds.has("anp-poco-categoria")) {
    addEdge(
      "axon-term-classificacao-poco",
      "anp-poco-categoria",
      "is_specialization_of",
      "é especialização de",
      "is specialization of",
      "axon_term_to_existing"
    );
  }
  if (axonIds.has("axon-term-classificacao-poco") && existingIds.has("poco")) {
    addEdge(
      "axon-term-classificacao-poco",
      "poco",
      "applies_to",
      "aplica-se a",
      "applies to",
      "axon_attr_bridge"
    );
  }

  /* ─── P. Acervo terms supplemental: amostra is part of acervo (done in §D).
     Add Operações em amostras (Assuntos) as is_part_of Domínio Acervo (already
     by §A parent_id). ─── */

  /* ─── Q. Objetivo do poço applies to poco ─── */
  if (axonIds.has("axon-term-objetivo-poco") && existingIds.has("poco")) {
    addEdge(
      "axon-term-objetivo-poco",
      "poco",
      "applies_to",
      "aplica-se a",
      "applies to",
      "axon_attr_bridge"
    );
  }

  /* ─── R0. Floating Domínios bridge to existing pivots so they don't become
     isolated components. Each bridge uses is_part_of in the inverse-of-mereology
     sense (existing pivot is part of the Domínio super-topic). ─── */

  // Aval. de formações e petrofísica → modelo-petrofisico, perfil-poco
  if (axonIds.has("axon-dom-aval-petrofisica") && existingIds.has("modelo-petrofisico")) {
    addEdge(
      "modelo-petrofisico",
      "axon-dom-aval-petrofisica",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_dom_link"
    );
  }
  if (axonIds.has("axon-dom-aval-petrofisica") && existingIds.has("perfil-poco")) {
    addEdge(
      "perfil-poco",
      "axon-dom-aval-petrofisica",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_dom_link"
    );
  }

  // Geofísica → sísmica (aquisição, processamento, horizonte)
  for (const id of [
    "seismic-acquisition-survey",
    "seismic-processing-project",
    "seismic-horizon",
  ]) {
    if (existingIds.has(id) && axonIds.has("axon-dom-geofisica")) {
      addEdge(
        id,
        "axon-dom-geofisica",
        "is_part_of",
        "faz parte de",
        "is part of",
        "axon_dom_link"
      );
    }
  }

  // Interpretação Exploratória → seismic-horizon, falha, idade-geologica, pag, qpg, GEOMEC072
  for (const id of ["seismic-horizon", "falha", "idade-geologica", "pag", "qpg", "GEOMEC072"]) {
    if (existingIds.has(id) && axonIds.has("axon-dom-interp-exploratoria")) {
      addEdge(
        id,
        "axon-dom-interp-exploratoria",
        "is_part_of",
        "faz parte de",
        "is part of",
        "axon_dom_link"
      );
    }
  }

  // Geodésia → existing operational/geographic pivots. There is no dedicated
  // datum node (datum lives in well-attributes.json as a format-only attr).
  // Bridge via the coordinate-keeping anchors we do have. The Axon definition
  // mentions IBGE/ANP geodesy; the closest existing nodes are `bacia-sedimentar`
  // (geographic), `uts` (regulatory anchor for surface units) and the Domínio
  // Aquisição (which depends on geodesy for coordinates). We bridge via the
  // axon-area-exploracao parent (already done in §A) plus a soft `supports`
  // link from Geodésia to Aquisição de dados geológicos.
  if (axonIds.has("axon-dom-geodesia") && axonIds.has("axon-dom-aquisicao-dados-geo")) {
    addEdge(
      "axon-dom-geodesia",
      "axon-dom-aquisicao-dados-geo",
      "supports",
      "apoia",
      "supports",
      "axon_dom_link"
    );
  }
  // Geodésia also supports Geofísica (coordinates & datum for seismic acquisition)
  if (axonIds.has("axon-dom-geodesia") && axonIds.has("axon-dom-geofisica")) {
    addEdge(
      "axon-dom-geodesia",
      "axon-dom-geofisica",
      "supports",
      "apoia",
      "supports",
      "axon_dom_link"
    );
  }

  /* ─── R. Amostragem de calha prevista is_part_of Programa de aquisição de dados
     (Subassunto). The hierarchy edge from §A handles the parent_id link to
     planejamento; here we add the direct semantic link to the Subassunto. ─── */
  if (
    axonIds.has("axon-term-amostragem-calha-prevista") &&
    axonIds.has("axon-sub-prog-aquisicao")
  ) {
    addEdge(
      "axon-term-amostragem-calha-prevista",
      "axon-sub-prog-aquisicao",
      "is_part_of",
      "faz parte de",
      "is part of",
      "axon_internal"
    );
  }
  // It also requires cuttings-sampling operation to execute
  if (axonIds.has("axon-term-amostragem-calha-prevista") && existingIds.has("cuttings-sampling")) {
    addEdge(
      "axon-term-amostragem-calha-prevista",
      "cuttings-sampling",
      "requires",
      "requer",
      "requires",
      "axon_to_op"
    );
  }

  return { nodes, edges };
}

/* ─────────────────────────────────────────────────────────────
 * SOURCE DATA — copiado de Geolytics src/config/dicionario.js
 * ───────────────────────────────────────────────────────────── */

const GLOSSARIO = [
  {
    id: "bloco",
    termo: "Bloco",
    categoria: "geologia",
    definicao:
      "Parte de uma bacia sedimentar, formada por um prisma vertical de profundidade indeterminada, com superfície poligonal definida pelas coordenadas geográficas de seus vértices, onde são desenvolvidas atividades de exploração ou produção de petróleo e gás natural.",
    fonte: "Lei nº 9478, de 06/08/1997",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
      "ranp-708",
      "ranp-815",
    ],
  },
  {
    id: "bacia-sedimentar",
    termo: "Bacia Sedimentar",
    categoria: "geologia",
    definicao:
      "Depressão da crosta terrestre onde se acumulam rochas sedimentares que podem ser portadoras de petróleo ou gás, associados ou não.",
    fonte: "Lei nº 9478, de 06/08/1997",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
    ],
  },
  {
    id: "bacias-agrupadas",
    termo: "Bacias Agrupadas",
    categoria: "geologia",
    definicao:
      "Agrupamento regional das bacias sedimentares em quatro grupos: Mar — Margem Equatorial (Foz do Amazonas, Pará-Maranhão, Barreirinhas, Ceará, Potiguar marítimo); Mar — Margem Leste (Pernambuco-Paraíba, Sergipe-Alagoas, Jacuípe, Camamu-Almada, Jequitinhonha, Cumuruxatiba, Mucuri, Espírito Santo, Campos, Santos, Pelotas); Terra — Bacias Maduras (Potiguar, Sergipe, Alagoas, Recôncavo, Espírito Santo terrestre); Terra — Bacias de Nova Fronteira (Amazonas, Paraná, Parnaíba, São Francisco, Solimões, Tucano Sul).",
    fonte: "ANP/SEP",
    apareceEm: ["pocos-exploratorios", "blocos-contrato", "pads-andamento", "pads-concluidos"],
  },
  {
    id: "ambiente",
    termo: "Ambiente",
    categoria: "geologia",
    definicao:
      "Localização por ambiente dos blocos exploratórios sob contrato: terra (onshore) ou mar (offshore). Distingue operações terrestres e marítimas para fins de classificação e monitoramento regulatório.",
    fonte: "ANP/SEP",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
    ],
  },
  {
    id: "presal",
    termo: "Pré-sal",
    categoria: "geologia",
    definicao:
      "Camada geológica localizada abaixo de uma extensa camada de sal no subsolo marítimo e terrestre. Identificar se um poço atingiu o pré-sal é informação estratégica para avaliar o potencial exploratório e enquadrar o regime contratual aplicável.",
    fonte: "ANP/SEP",
    apareceEm: ["pocos-exploratorios"],
  },
  {
    id: "operador",
    termo: "Operador",
    categoria: "contratos",
    definicao:
      "Empresa legalmente designada pelos consorciados para conduzir e executar todas as operações e atividades na área sob contrato, de acordo com o estabelecido no contrato de E&P celebrado entre a contratante e o contratado.",
    fonte: "ANP/SEP",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
      "ranp-708",
      "ranp-815",
    ],
  },
  {
    id: "contratados",
    termo: "Contratados",
    categoria: "contratos",
    definicao:
      "Empresas contratadas e sua participação, em porcentagem, no contrato de E&P. Inclui o operador e eventuais parceiros do consórcio, com suas respectivas parcelas de participação.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato", "pads-andamento"],
  },
  {
    id: "contrato-ep",
    termo: "Contrato de E&P",
    categoria: "contratos",
    definicao:
      "Contrato de Exploração e Produção assinado entre o agente econômico e a ANP. Estabelece os direitos e obrigações das partes para exploração de petróleo e gás natural em um bloco específico, incluindo o Programa Exploratório Mínimo (PEM) e as condições de produção.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato", "ranp-708", "ranp-815"],
  },
  {
    id: "pem",
    termo: "PEM — Programa Exploratório Mínimo",
    categoria: "contratos",
    definicao:
      "Conjunto mínimo de atividades exploratórias que o contratado se compromete a realizar como parte do contrato de concessão ou partilha de produção. A partir da 5ª Rodada (2003), o PEM do 1º período exploratório é expresso em Unidades de Trabalho (UTs) — parâmetro de oferta na licitação — e o do 2º período corresponde obrigatoriamente à perfuração de um poço exploratório. O cumprimento de cada período é garantido por garantia financeira prestada à ANP, devolvida após a entrega dos dados conforme padrões regulatórios.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato"],
  },
  {
    id: "pte",
    termo: "PTE — Plano de Trabalho Exploratório",
    categoria: "contratos",
    definicao:
      "Instrumento de acompanhamento e fiscalização das atividades exploratórias de cada bloco sob contrato de E&P, substituto do Programa Anual de Trabalho e Orçamento e do Plano de Exploração. Deve ser apresentado em até 90 dias da assinatura do contrato de concessão (ou 180 dias no caso de partilha de produção). Ao longo da vigência, o operador envia anualmente: o PTE previsto (outubro) e o PTE realizado (março). Revisões são permitidas conforme condições da Resolução ANP nº 876/2022. A ANP analisa e aprova cada remessa em até 30 dias. O envio é realizado pelo sistema DPP.",
    fonte: "Resolução ANP nº 876/2022",
    apareceEm: ["blocos-contrato"],
  },
  {
    id: "periodo-exploratorio",
    termo: "Período Exploratório",
    categoria: "contratos",
    definicao:
      "Identificação do período exploratório dos blocos sob contrato: 1º, 2º ou 3º período exploratório, período único ou prorrogado por PAD. Cada período tem prazo definido e obrigações exploratórias mínimas que o contratado deve cumprir.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato"],
  },
  {
    id: "uts",
    termo: "UTS — Unidades de Trabalho",
    categoria: "contratos",
    definicao:
      "Unidade de conversão para diferentes trabalhos exploratórios, utilizada para fins de aferição da execução do Programa Exploratório Mínimo (PEM) de cada contrato. Permite comparar diferentes tipos de atividades exploratórias — como perfuração de poços, aquisição sísmica e estudos técnicos — em uma unidade comum.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato"],
  },
  {
    id: "fase-exploratoria",
    termo: "Fase Exploratória",
    categoria: "contratos",
    definicao:
      "Período total da fase de exploração do bloco contratado. O vencimento da fase exploratória pode ser igual ao vencimento do último período exploratório ou ao vencimento do último PAD, quando a fase estiver prorrogada por plano de avaliação de descobertas.",
    fonte: "ANP/SEP",
    apareceEm: ["blocos-contrato"],
  },
  {
    id: "etapa-prorrogada",
    termo: "Etapa Prorrogada",
    categoria: "contratos",
    definicao:
      "Identifica a etapa do período exploratório que foi prorrogada com base em resolução específica da ANP. Pode ser: período único, 1º e 2º PE conjuntamente, ou apenas o 2º PE.",
    fonte: "ANP/SEP",
    apareceEm: ["ranp-708", "ranp-815"],
  },
  {
    id: "regime-contratual",
    termo: "Regime Contratual",
    categoria: "contratos",
    definicao:
      "Modalidade contratual do bloco exploratório. Concessão: o concessionário assume todos os riscos e detém o petróleo produzido mediante pagamento de tributos. Partilha de produção: o petróleo produzido é dividido entre o contratado e a União, sendo a Petrobras operadora obrigatória nos blocos do pré-sal.",
    fonte: "ANP/SEP",
    apareceEm: ["pads-andamento", "pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "pad",
    termo: "PAD — Plano de Avaliação de Descobertas",
    categoria: "operacoes",
    definicao:
      "Instrumento pelo qual o concessionário avalia tecnicamente uma descoberta de hidrocarbonetos para determinar sua viabilidade comercial. Elaborado e entregue à ANP conforme a Resolução ANP nº 845/2021, descreve a descoberta e apresenta programa de trabalho com atividades, prazos e investimentos para avaliação. O código do PAD corresponde ao nome da acumulação principal da área avaliada. Após a conclusão, o PAD resulta em RFAD; se a descoberta for comercial, o RFAD fundamenta a Declaração de Comercialidade.",
    fonte: "ANP/SEP — SIGEP; Resolução ANP nº 845/2021",
    apareceEm: ["pads-andamento", "pads-concluidos", "declaracoes-comercialidade", "ranp-815"],
  },
  {
    id: "rfad",
    termo: "RFAD — Relatório Final de Avaliação de Descobertas",
    categoria: "operacoes",
    definicao:
      "Documento de encerramento do PAD que consolida as atividades de avaliação realizadas e os resultados da interpretação dos dados. A aprovação do RFAD pela ANP é condição necessária para conferir efetividade a uma eventual Declaração de Comercialidade. Em caso de resultado negativo, encerra o PAD sem declaração.",
    fonte: "Resolução ANP nº 845/2021",
    apareceEm: ["pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "poco-anp",
    termo: "Poço ANP",
    categoria: "operacoes",
    definicao:
      "Identificador padronizado atribuído a um poço de petróleo ou gás no Brasil, conforme as regras da Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP). Permite a identificação única em documentos técnicos, sistemas oficiais e comunicações regulatórias.",
    fonte: "ANP/SEP",
    apareceEm: ["pocos-exploratorios", "blocos-contrato"],
  },
  {
    id: "notificacao-descoberta",
    termo: "Notificação de Descoberta",
    categoria: "operacoes",
    definicao:
      "Registro que identifica se ocorreu ou não indícios de hidrocarbonetos durante a perfuração de um poço exploratório. A data da primeira descoberta registra quando foi notificada à ANP a primeira detecção de hidrocarbonetos no poço.",
    fonte: "ANP/SEP — SIGEP",
    apareceEm: ["pocos-exploratorios"],
  },
  {
    id: "declaracao-comercialidade",
    termo: "Declaração de Comercialidade",
    categoria: "operacoes",
    definicao:
      "Declaração formal do concessionário à ANP de que uma descoberta de hidrocarbonetos possui viabilidade econômica para produção. Encerra o PAD com resultado positivo e dá início ao planejamento da área de desenvolvimento.",
    fonte: "ANP/SEP — SIGEP",
    apareceEm: ["pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "area-desenvolvimento",
    termo: "Área de Desenvolvimento da Produção",
    categoria: "operacoes",
    definicao:
      'Fase intermediária do ciclo de E&P entre a Declaração de Comercialidade e o Primeiro Óleo. Durante essa etapa, o concessionário executa o Plano de Desenvolvimento (PD) aprovado pela ANP: contratação de plataformas, perfuração de poços produtores, instalação de sistemas submarinos e gasodutos. O campo é considerado "em desenvolvimento" enquanto a produção comercial ainda não se iniciou.',
    fonte: "Lei nº 9.478/1997; RANP 810/2020",
    apareceEm: ["pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "plano-desenvolvimento",
    termo: "Plano de Desenvolvimento",
    categoria: "operacoes",
    definicao:
      "Documento técnico-econômico obrigatório entregue pelo concessionário à ANP em até 180 dias após a Declaração de Comercialidade. Agrupa informações técnicas, operacionais, econômicas e ambientais da explotação do campo, incluindo abandono. A ANP analisa o PD em até 180 dias; se solicitar modificações, o contratado tem 60 dias para apresentar o PD modificado. Após aprovação, o PD passa a vincular a atuação do concessionário. Em casos de jazidas compartilhadas, deve ser acompanhado do AIP ou do CIP.",
    fonte: "Resolução ANP nº 17/2015",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "aip",
    termo: "AIP — Acordo de Individualização da Produção",
    categoria: "operacoes",
    definicao:
      "Acordo celebrado entre concessionários de blocos distintos que compartilham a mesma jazida de hidrocarbonetos, estabelecendo os termos para a produção individualizada de cada parte. Deve ser submetido à ANP juntamente com o Plano de Desenvolvimento quando houver descoberta em jazida compartilhada. Em situações em que o AIP ainda não está concluído, o CIP pode ser apresentado em substituição provisória.",
    fonte: "Lei nº 9.478/1997; Resolução ANP nº 17/2015",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "cip",
    termo: "CIP — Compromisso de Individualização da Produção",
    categoria: "operacoes",
    definicao:
      "Instrumento provisório apresentado pelos concessionários à ANP quando o Acordo de Individualização da Produção (AIP) ainda não foi concluído, comprometendo-se a celebrá-lo em prazo definido. Acompanha o Plano de Desenvolvimento em casos de jazida compartilhada nos quais o AIP definitivo não está disponível.",
    fonte: "Lei nº 9.478/1997; Resolução ANP nº 17/2015",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "primeiro-oleo",
    termo: "Primeiro Óleo",
    categoria: "operacoes",
    definicao:
      "Marco que sinaliza o início da produção comercial em um campo. Para a ANP, é o evento que encerra formalmente a Fase de Desenvolvimento da Produção e inaugura o Campo de Produção. A partir desse ponto, o operador passa a submeter o Programa Anual de Produção (PAP) e a pagar royalties sobre a produção.",
    fonte: "ANP/SEP",
    apareceEm: [],
  },
  {
    id: "teste-formacao",
    termo: "Teste de Formação",
    categoria: "operacoes",
    definicao:
      "Teste realizado por tubulação com fluxo em superfície para avaliação do reservatório e coleta de amostras de fluido. Abrange os tipos: TIF (identificação de fluidos), TF (poço aberto), TFS (seletivo a poço aberto), TFR (poço revestido) e TFRE (TFR estendido > 72 h). Não exige autorização prévia da ANP, exceto quando realizado no âmbito de PAD ou PD ainda não aprovado. Exige envio do RFTP via DPP em até 60 dias após conclusão. Durante a execução, o operador reporta diariamente via SOP no i-Engine.",
    fonte: "ANP — Norma de Testes de Poço; Resolução ANP nº 71/2014",
    apareceEm: ["pads-andamento", "pads-concluidos"],
  },
  {
    id: "tld",
    termo: "TLD",
    categoria: "operacoes",
    definicao:
      "Teste de Longa Duração. Realizado dentro de um PAD, com duração total superior a 72 horas de fluxo. Exige autorização prévia específica da ANP, mesmo em PAD aprovado. Sujeito ao pagamento de royalties e participações governamentais. Requer aprovação do sistema de medição fiscal e destino da produção. Documentação obrigatória: TLDI (em até 1 dia após abertura do poço), TLDS (semanal) e TLDF (em até 7 dias após conclusão), todos enviados via i-Engine; além do BMP mensal e RFTP. Internacionalmente corresponde ao Extended Well Test (EWT).",
    fonte: "ANP — Norma de Testes de Poço (TLD)",
    apareceEm: ["pads-andamento", "pads-concluidos"],
  },
  {
    id: "rftp",
    termo: "RFTP",
    categoria: "regulatorio",
    definicao:
      "Relatório Final de Teste de Poço. Documento obrigatório enviado à ANP via DPP em até 60 dias após a conclusão de qualquer teste de formação (TIF, TF, TFS, TFR, TFRE, TLD). Contém: relatório operacional (sequência de eventos), planilhas de medições de superfície, relatório de estimulação, esquema de coluna de teste e dados de registradores de fundo.",
    fonte: "ANP — Norma de Testes de Poço",
    apareceEm: [],
  },
  {
    id: "i-engine",
    termo: "i-Engine",
    categoria: "sistemas",
    definicao:
      "Sistema de webservices da ANP para envio e recebimento de dados técnicos de E&P. Utilizado para: SOP (Situação Operacional de Poços) durante testes de formação, TLDI/TLDS/TLDF durante TLD e BMP mensal na fase de produção. Utiliza formato XML padronizado com tags semânticas para amostra, fase e componente conforme Resolução ANP nº 880/2022.",
    fonte: "ANP/SEP — Resolução nº 880/2022",
    apareceEm: ["pads-andamento", "pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "dpp",
    termo: "DPP",
    categoria: "sistemas",
    definicao:
      "Portal de Dados e Projetos da ANP. Sistema utilizado para envio do RFTP e respectivos anexos após a conclusão de testes de formação e TLD. Complementa o i-Engine no fluxo regulatório de entrega de dados técnicos de poço.",
    fonte: "ANP/SEP",
    apareceEm: [],
  },
  {
    id: "bmp",
    termo: "BMP",
    categoria: "regulatorio",
    definicao:
      "Boletim Mensal de Produção. Documento enviado mensalmente à ANP via i-Engine durante a realização de TLD e na fase de produção regular do campo. Informa volumes de óleo, gás e outros fluidos produzidos para efeito de cálculo de royalties e participações governamentais.",
    fonte: "ANP/SEP",
    apareceEm: ["declaracoes-comercialidade"],
  },
  {
    id: "rodada-licitacao",
    termo: "Rodada de Licitação",
    categoria: "regulatorio",
    definicao:
      "Ato pelo qual o governo leiloa áreas específicas do seu território para fins de exploração mineral. Identifica em qual rodada o bloco exploratório foi arrematado, permitindo rastrear o histórico de concessões e partilhas no Brasil.",
    fonte: "Dicionário enciclopédico inglês-português de geofísica e geologia",
    apareceEm: ["pads-andamento", "pads-concluidos", "declaracoes-comercialidade"],
  },
  {
    id: "processo-sancionador",
    termo: "Processo Sancionador",
    categoria: "regulatorio",
    definicao:
      "Processo administrativo resultante da consolidação das autuações relativas à exploração de petróleo e gás natural em trâmite na Superintendência de Exploração (SEP). Registra o auto de infração, o motivo da autuação, a multa aplicada e a situação processual.",
    fonte: "ANP/SEP",
    apareceEm: ["processos-sancionadores"],
  },
  {
    id: "anp",
    termo: "ANP",
    categoria: "regulatorio",
    definicao:
      "Agência Nacional do Petróleo, Gás Natural e Biocombustíveis. Autarquia federal vinculada ao Ministério de Minas e Energia, responsável pela regulação, contratação e fiscalização das atividades da indústria de petróleo, gás natural e biocombustíveis no Brasil.",
    fonte: "Lei nº 9478/1997",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
      "processos-sancionadores",
      "ranp-708",
      "ranp-815",
    ],
  },
  {
    id: "sigep",
    termo: "SIGEP",
    categoria: "sistemas",
    definicao:
      "Sistema de Informações Gerenciais de Exploração e Produção. Sistema oficial da ANP que concentra e disponibiliza dados sobre poços, PADs, blocos e contratos de exploração e produção de petróleo e gás natural no Brasil.",
    fonte: "ANP/SEP",
    apareceEm: ["pocos-exploratorios", "blocos-contrato", "pads-andamento", "pads-concluidos"],
  },
  {
    id: "sep",
    termo: "SEP",
    categoria: "sistemas",
    definicao:
      "Superintendência de Exploração da ANP. Unidade organizacional responsável pelo gerenciamento e fiscalização das atividades exploratórias de petróleo e gás natural no Brasil, incluindo o acompanhamento de blocos, poços e PADs.",
    fonte: "ANP",
    apareceEm: [
      "pocos-exploratorios",
      "blocos-contrato",
      "pads-andamento",
      "pads-concluidos",
      "declaracoes-comercialidade",
      "processos-sancionadores",
      "ranp-708",
      "ranp-815",
    ],
  },
];

const CONJUNTOS = [
  {
    id: "pocos-exploratorios",
    titulo: "Poços Exploratórios em Blocos",
    descricao:
      "Dados gerais sobre os poços exploratórios que tiveram a perfuração iniciada a partir do ano de 1998.",
    fonte: "ANP/SEP — SIGEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      {
        nome: "POÇO ANP",
        descricao: "Identificador padronizado do poço conforme regras da ANP",
        tipo: "TEXT",
      },
      { nome: "BLOCO", descricao: "Nome do bloco onde o poço foi perfurado", tipo: "TEXT" },
      { nome: "BACIA", descricao: "Nome da bacia sedimentar", tipo: "TEXT" },
      {
        nome: "BACIAS AGRUPADAS",
        descricao: "Agrupamento regional das bacias sedimentares",
        tipo: "TEXT",
      },
      { nome: "ESTADO", descricao: "Unidade da Federação", tipo: "TEXT" },
      { nome: "AMBIENTE", descricao: "Localização por ambiente: terra ou mar", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      {
        nome: "INÍCIO DA PERFURAÇÃO",
        descricao: "Data em que a perfuração do poço teve início",
        tipo: "DATE",
      },
      {
        nome: "CONCLUSÃO DA PERFURAÇÃO",
        descricao: "Data em que foi concluída a perfuração",
        tipo: "DATE",
      },
      {
        nome: "PROFUNDIDADE FINAL (m)",
        descricao: "Profundidade final alcançada pelo poço, em metros",
        tipo: "INTEGER",
      },
      {
        nome: "ATINGIU PRÉ-SAL?",
        descricao: "Identifica se o poço atingiu o pré-sal",
        tipo: "TEXT",
      },
      {
        nome: "NOTIFICAÇÃO DE DESCOBERTA?",
        descricao: "Identifica se ocorreu indícios de hidrocarbonetos durante a perfuração",
        tipo: "TEXT",
      },
      {
        nome: "DATA DA 1ª DESCOBERTA",
        descricao: "Data da primeira descoberta de hidrocarbonetos notificada à ANP",
        tipo: "DATE",
      },
      {
        nome: "FLUIDO NOTIFICAÇÃO DE DESCOBERTA",
        descricao: "Hidrocarboneto que foi notificada a descoberta à ANP",
        tipo: "TEXT",
      },
    ],
  },
  {
    id: "blocos-contrato",
    titulo: "Blocos sob Contrato",
    descricao:
      "Dados gerais sobre os blocos exploratórios sob contrato: operador, contratados, bacia, período exploratório, prazos de vencimento e dados técnicos sobre poços e UTS.",
    fonte: "ANP/SEP — SIGEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      { nome: "BLOCO", descricao: "Nome do bloco exploratório", tipo: "TEXT" },
      {
        nome: "CONTRATO",
        descricao: "Código do contrato de E&P assinado com a ANP",
        tipo: "INTEGER",
      },
      {
        nome: "OPERADOR",
        descricao: "Concessionário designado para conduzir as operações",
        tipo: "TEXT",
      },
      {
        nome: "CONTRATADOS",
        descricao: "Empresas contratadas e sua participação percentual",
        tipo: "TEXT",
      },
      { nome: "AMBIENTE", descricao: "Localização por ambiente: terra ou mar", tipo: "TEXT" },
      {
        nome: "BACIAS AGRUPADAS",
        descricao: "Agrupamento regional das bacias sedimentares",
        tipo: "TEXT",
      },
      { nome: "BACIA", descricao: "Nome da bacia sedimentar", tipo: "TEXT" },
      {
        nome: "ÁREA (MIL km²)",
        descricao: "Área do bloco em mil quilômetros quadrados",
        tipo: "DECIMAL",
      },
      { nome: "RODADA", descricao: "Identificação da rodada de licitação", tipo: "TEXT" },
      {
        nome: "PERÍODO",
        descricao: "Identificação do período exploratório: 1º, 2º, 3º ou único",
        tipo: "TEXT",
      },
      {
        nome: "PRESENÇA PAD",
        descricao: "Indica se há ou houve Plano de Avaliação de Descobertas",
        tipo: "TEXT",
      },
      {
        nome: "DATA DA ASSINATURA CONTRATO",
        descricao: "Data de assinatura do contrato de E&P",
        tipo: "DATE",
      },
      {
        nome: "DATA INÍCIO SUSPENSÃO",
        descricao: "Data de início da suspensão do contrato",
        tipo: "DATE",
      },
      {
        nome: "1º PE VENCIMENTO",
        descricao: "Data de vencimento do 1º período exploratório",
        tipo: "DATE",
      },
      {
        nome: "2º PE VENCIMENTO",
        descricao: "Data de vencimento do 2º período exploratório",
        tipo: "DATE",
      },
      {
        nome: "3º PE VENCIMENTO",
        descricao: "Data de vencimento do 3º período exploratório",
        tipo: "DATE",
      },
      {
        nome: "ÚLTIMO PAD VENCIMENTO",
        descricao: "Data de vencimento do último PAD",
        tipo: "DATE",
      },
      {
        nome: "FASE EXPLORATÓRIA VENCIMENTO",
        descricao: "Data de vencimento da fase exploratória do bloco",
        tipo: "DATE",
      },
      {
        nome: "UTS COMPROMISSADAS",
        descricao: "Unidades de Trabalho comprometidas no Programa Exploratório Mínimo",
        tipo: "DECIMAL",
      },
      {
        nome: "QTD DE POÇOS PERFURADOS",
        descricao: "Número de poços perfurados na área contratada",
        tipo: "INTEGER",
      },
      {
        nome: "POÇOS PERFURADOS",
        descricao: "Nome(s) dos poços ANP perfurados na área contratada",
        tipo: "TEXT",
      },
    ],
  },
  {
    id: "pads-andamento",
    titulo: "PADs em Andamento",
    descricao:
      "Dados gerais sobre os Planos de Avaliação de Descobertas (PADs) atualmente em andamento na fase de exploração.",
    fonte: "ANP/SEP — SIGEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      {
        nome: "CÓDIGO DO PAD",
        descricao: "Nome do PAD — corresponde à acumulação principal da área",
        tipo: "TEXT",
      },
      { nome: "BLOCO", descricao: "Nome do bloco exploratório", tipo: "TEXT" },
      { nome: "BACIA", descricao: "Nome da bacia sedimentar", tipo: "TEXT" },
      {
        nome: "BACIAS AGRUPADAS",
        descricao: "Agrupamento regional das bacias sedimentares",
        tipo: "TEXT",
      },
      { nome: "AMBIENTE", descricao: "Localização por ambiente: terra ou mar", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      {
        nome: "CONTRATADOS",
        descricao: "Empresas contratadas e sua participação percentual",
        tipo: "TEXT",
      },
      { nome: "RODADA", descricao: "Identificação da rodada de licitação", tipo: "TEXT" },
      {
        nome: "REGIME CONTRATUAL",
        descricao: "Modalidade contratual: Concessão ou Partilha",
        tipo: "TEXT",
      },
      { nome: "SITUAÇÃO", descricao: "Situação atual do PAD", tipo: "TEXT" },
      { nome: "INÍCIO EFETIVO", descricao: "Data do início efetivo do PAD", tipo: "DATE" },
      { nome: "TÉRMINO PREVISTO", descricao: "Data do término previsto do PAD", tipo: "DATE" },
    ],
  },
  {
    id: "pads-concluidos",
    titulo: "PADs Concluídos",
    descricao:
      "Dados gerais sobre os Planos de Avaliação de Descobertas (PADs) concluídos na fase de exploração, incluindo resultado de comercialidade e área de desenvolvimento.",
    fonte: "ANP/SEP — SIGEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      {
        nome: "CÓDIGO DO PAD",
        descricao: "Nome do PAD — corresponde à acumulação principal da área",
        tipo: "TEXT",
      },
      { nome: "BLOCO", descricao: "Nome do bloco exploratório", tipo: "TEXT" },
      { nome: "BACIA", descricao: "Nome da bacia sedimentar", tipo: "TEXT" },
      { nome: "AMBIENTE", descricao: "Localização por ambiente: terra ou mar", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      { nome: "RODADA", descricao: "Identificação da rodada de licitação", tipo: "TEXT" },
      {
        nome: "REGIME CONTRATUAL",
        descricao: "Modalidade contratual: Concessão ou Partilha",
        tipo: "TEXT",
      },
      { nome: "INÍCIO EFETIVO", descricao: "Data do início efetivo do PAD", tipo: "DATE" },
      { nome: "TÉRMINO EFETIVO", descricao: "Data do término efetivo do PAD", tipo: "DATE" },
      {
        nome: "DECLAROU COMERCIALIDADE",
        descricao: "Identifica se ocorreu declaração de comercialidade: Sim ou Não",
        tipo: "TEXT",
      },
      {
        nome: "ÁREA DE DESENVOLVIMENTO",
        descricao: "Nome da área de desenvolvimento resultante",
        tipo: "TEXT",
      },
    ],
  },
  {
    id: "declaracoes-comercialidade",
    titulo: "Declarações de Comercialidade",
    descricao:
      "Dados gerais sobre as Declarações de Comercialidade nos blocos sob contrato na fase de exploração.",
    fonte: "ANP/SEP — SIGEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      {
        nome: "CÓDIGO DO PAD",
        descricao: "Nome do PAD — corresponde à acumulação principal da área",
        tipo: "TEXT",
      },
      {
        nome: "BLOCO(S)",
        descricao: "Nome(s) do(s) bloco(s) relacionado(s) à declaração",
        tipo: "TEXT",
      },
      { nome: "BACIA", descricao: "Nome da bacia sedimentar", tipo: "TEXT" },
      { nome: "AMBIENTE", descricao: "Localização por ambiente: terra ou mar", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      { nome: "RODADA", descricao: "Identificação da rodada de licitação", tipo: "TEXT" },
      {
        nome: "REGIME CONTRATUAL",
        descricao: "Modalidade contratual: Concessão ou Partilha",
        tipo: "TEXT",
      },
      {
        nome: "DATA DA DECLARAÇÃO DE COMERCIALIDADE",
        descricao: "Data da declaração de comercialidade",
        tipo: "DATE",
      },
      {
        nome: "ÁREA DE DESENVOLVIMENTO",
        descricao: "Nome da área de desenvolvimento resultante",
        tipo: "TEXT",
      },
    ],
  },
  {
    id: "processos-sancionadores",
    titulo: "Processos Sancionadores",
    descricao:
      "Dados gerais referente à situação dos Processos Sancionadores de exploração de petróleo e gás natural em trâmite na SEP.",
    fonte: "ANP/SEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      { nome: "EMPRESA", descricao: "Nome da empresa autuada", tipo: "TEXT" },
      { nome: "CNPJ/CPF", descricao: "Número do CNPJ ou CPF do contratado", tipo: "TEXT" },
      { nome: "Nº PROCESSO", descricao: "Número do processo administrativo", tipo: "TEXT" },
      { nome: "Nº DF", descricao: "Número do documento de fiscalização", tipo: "TEXT" },
      { nome: "DATA DO AUTO", descricao: "Data do auto de infração", tipo: "DATE" },
      { nome: "MOTIVO", descricao: "Fundamentação que deu ensejo à autuação", tipo: "TEXT" },
      {
        nome: "SITUAÇÃO PROCESSUAL",
        descricao: "Situação do andamento do processo administrativo",
        tipo: "TEXT",
      },
      {
        nome: "MULTA APLICADA",
        descricao: "Valor da multa aplicada como resultado do processo",
        tipo: "DECIMAL",
      },
      { nome: "RECURSO", descricao: "Indica se houve recurso ao processo", tipo: "TEXT" },
    ],
  },
  {
    id: "ranp-708",
    titulo: "Resolução ANP nº 708/2017",
    descricao:
      "Dados sobre blocos exploratórios com período exploratório prorrogado pela Resolução ANP nº 708/2017.",
    fonte: "ANP/SEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      { nome: "BLOCO", descricao: "Nome do bloco exploratório", tipo: "TEXT" },
      { nome: "CONTRATO", descricao: "Nome fantasia do contrato de E&P", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      {
        nome: "ETAPA PRORROGADA",
        descricao: "Etapa prorrogada: período único, 1º e 2º PE, ou 2º PE",
        tipo: "TEXT",
      },
      {
        nome: "DATA DE ADESÃO À RESOLUÇÃO",
        descricao: "Data na qual se deu a adesão à Resolução nº 708/2017",
        tipo: "DATE",
      },
    ],
  },
  {
    id: "ranp-815",
    titulo: "Resolução ANP nº 815/2020",
    descricao:
      "Dados sobre blocos exploratórios com período exploratório prorrogado pela Resolução ANP nº 815/2020.",
    fonte: "ANP/SEP",
    formato: "CSV",
    frequencia: "Mensal",
    contato: "sigep_sep@anp.gov.br",
    colunas: [
      { nome: "BLOCO", descricao: "Nome do bloco exploratório", tipo: "TEXT" },
      { nome: "CONTRATO", descricao: "Nome fantasia do contrato de E&P", tipo: "TEXT" },
      { nome: "OPERADOR", descricao: "Empresa operadora do contrato de E&P", tipo: "TEXT" },
      {
        nome: "ETAPA PRORROGADA",
        descricao: "Etapa prorrogada: período único, 1º e 2º PE, ou 2º PE",
        tipo: "TEXT",
      },
      {
        nome: "PAD",
        descricao: "Nome do Plano de Avaliação de Descobertas associado à prorrogação",
        tipo: "TEXT",
      },
      {
        nome: "DATA DE ADESÃO À RESOLUÇÃO",
        descricao: "Data na qual se deu a adesão à Resolução nº 815/2020",
        tipo: "DATE",
      },
    ],
  },
];

/* 3W: register dataset entry */
CONJUNTOS.push(THREEW_DATASET);

const ONTOLOGY_TYPES = {
  tipologia: {
    label: "Tipologia do Dado",
    desc: "O que o dado representa quimicamente/operacionalmente",
    items: [
      {
        id: "geo_org",
        label: "Geoquímica Orgânica",
        desc: "TOC, pirólise, biomarcadores, maturidade",
      },
      { id: "geo_inorg", label: "Geoquímica Inorgânica", desc: "Isótopos, traços inorgânicos" },
      { id: "geo_hidro", label: "Hidrogeoquímica", desc: "Análise de água de formação" },
      { id: "pvt", label: "PVT", desc: "Propriedades pressão-volume-temperatura" },
      { id: "show", label: "Show de Fluido", desc: "Observação visual em perfuração" },
      { id: "teste", label: "Teste de Formação", desc: "DST, teste de produção" },
      { id: "composicao", label: "Composição Molecular", desc: "GC, GC-MS, espectrometria" },
    ],
  },
  nivel: {
    label: "Nível de Processamento",
    desc: "Grau de transformação do dado bruto ao produto analítico",
    items: [
      {
        id: "primario",
        label: "Dado Primário",
        desc: "Medida direta de amostra ou análise laboratorial",
      },
      {
        id: "interpretado",
        label: "Dado Interpretado",
        desc: "Classificação, mapa ou modelo derivado das medidas",
      },
      { id: "curado", label: "Produto Curado", desc: "Dataset validado, harmonizado e versionado" },
    ],
  },
};

const DOMAINS = [
  { id: "ativos", label: "Ativos", desc: "Blocos, campos, concessões, PADs, regulatório ANP" },
  {
    id: "fluidos",
    label: "Fluidos",
    desc: "Produção e injeção — óleo, gás, água, condensado, CO2, vapor",
  },
  {
    id: "rocha",
    label: "Rocha",
    desc: "Bacias sedimentares, formações, estratigrafia, ambiente deposicional",
  },
  {
    id: "geomecanica",
    label: "Geomecânica",
    desc: "Profundidade, estratificação, stress in-situ (em roadmap)",
  },
];

/* ─────────────────────────────────────────────────────────────
 * ENTITY GRAPH — nós por entidade (não por domínio)
 * ───────────────────────────────────────────────────────────── */

const COLORS = {
  operational: "#378ADD",
  contractual: "#7F77DD",
  actor: "#D85A30",
  instrument: "#888780",
  geological: "#639922",
  equipment: "#C77B30",
  analytical: "#E67E22",
};
const SIZES = {
  operational: 28,
  contractual: 24,
  actor: 24,
  instrument: 20,
  geological: 20,
  equipment: 22,
  analytical: 20,
};

/* Mapa: id-entidade-grafo → glossario_id (quando existe) */
const ENTITY_NODES = [
  /* operational */
  {
    id: "poco",
    label: "Poço",
    label_en: "Well",
    type: "operational",
    glossId: "poco-anp",
    primary_key: "nome_anp",
    primary_key_standard: "ANP/SEP nomenclature",
    primary_key_pattern: "^[1-9]-[A-Z]+-[0-9]+[A-Z]?(-[A-Z]+)?$",
    /* Q7 (PR follow-up): Poço é âncora física e temporal — não classifica
       datasets. As referências OGEOMEC.Poco / FRX.Poco / DRX.Poco vivem
       agora como edges explícitas (ogeomec/frx/drx → poco) e em
       data/operacoes-geologicas.json#context_fields.Poco (FK source-of-truth). */
  },
  { id: "bloco", label: "Bloco", label_en: "Block", type: "operational", glossId: "bloco" },
  {
    id: "campo",
    label: "Campo",
    label_en: "Field",
    type: "operational",
    glossId: null,
    definicaoOverride:
      "Área produtora de petróleo ou gás natural a partir de um ou mais reservatórios contínuos. No regime ANP, um campo é declarado a partir da Declaração de Comercialidade que confirma a viabilidade econômica da descoberta.",
    fonte: "ANP/SEP",
  },
  {
    id: "bacia-sedimentar",
    label: "Bacia Sedimentar",
    label_en: "Sedimentary Basin",
    type: "operational",
    glossId: "bacia-sedimentar",
  },

  /* geological extension (extended-terms) */
  {
    id: "reservatorio",
    label: "Reservatório",
    label_en: "Reservoir",
    type: "operational",
    glossId: null,
    extendedId: "reservatorio",
  },
  {
    id: "formacao",
    label: "Formação",
    label_en: "Geological Formation",
    type: "geological",
    glossId: null,
    extendedId: "formacao-geologica",
  },
  {
    id: "sistema-deposicional",
    label: "Sistema Deposicional",
    label_en: "Depositional System",
    type: "geological",
    glossId: null,
    extendedId: "sistema-deposicional",
  },

  /* contractual */
  {
    id: "contrato-ep",
    label: "Contrato E&P",
    label_en: "E&P Contract",
    type: "contractual",
    glossId: "contrato-ep",
  },
  {
    id: "pem",
    label: "PEM",
    label_en: "Minimum Exploratory Programme",
    type: "contractual",
    glossId: "pem",
  },
  {
    id: "pte",
    label: "PTE",
    label_en: "Exploratory Work Plan",
    type: "contractual",
    glossId: "pte",
  },
  {
    id: "pad",
    label: "PAD",
    label_en: "Discovery Evaluation Plan",
    type: "contractual",
    glossId: "pad",
  },
  {
    id: "rfad",
    label: "RFAD",
    label_en: "Discovery Evaluation Final Report",
    type: "contractual",
    glossId: "rfad",
  },
  {
    id: "rodada-licitacao",
    label: "Rodada de Licitação",
    label_en: "Bid Round",
    type: "contractual",
    glossId: "rodada-licitacao",
  },
  {
    id: "declaracao-comercialidade",
    label: "Declaração de Comercialidade",
    label_en: "Commerciality Declaration",
    type: "contractual",
    glossId: "declaracao-comercialidade",
  },

  /* actor */
  { id: "operador", label: "Operador", label_en: "Operator", type: "actor", glossId: "operador" },
  {
    id: "anp",
    label: "ANP",
    label_en: "ANP (Brazilian Oil & Gas Regulator)",
    type: "actor",
    glossId: "anp",
  },

  /* instrument */
  {
    id: "sigep",
    label: "SIGEP",
    label_en: "SIGEP (E&P Information System)",
    type: "instrument",
    glossId: "sigep",
  },
  {
    id: "sep",
    label: "SEP",
    label_en: "SEP (ANP Exploration Office)",
    type: "instrument",
    glossId: "sep",
  },
  { id: "uts", label: "UTS", label_en: "Work Units", type: "instrument", glossId: "uts" },
  {
    id: "regime-contratual",
    label: "Regime Contratual",
    label_en: "Contract Regime",
    type: "instrument",
    glossId: "regime-contratual",
  },
  {
    id: "periodo-exploratorio",
    label: "Período Exploratório",
    label_en: "Exploratory Period",
    type: "instrument",
    glossId: "periodo-exploratorio",
  },
  {
    id: "processo-sancionador",
    label: "Processo Sancionador",
    label_en: "Sanctioning Proceeding",
    type: "instrument",
    glossId: "processo-sancionador",
  },
  {
    id: "notificacao-descoberta",
    label: "Notificação Descoberta",
    label_en: "Discovery Notification",
    type: "instrument",
    glossId: "notificacao-descoberta",
  },
  {
    id: "area-desenvolvimento",
    label: "Área de Desenvolvimento da Produção",
    label_en: "Production Development Phase",
    type: "contractual",
    glossId: "area-desenvolvimento",
  },
  {
    id: "plano-desenvolvimento",
    label: "Plano de Desenvolvimento",
    label_en: "Development Plan",
    type: "contractual",
    glossId: "plano-desenvolvimento",
  },
  {
    id: "aip",
    label: "AIP",
    label_en: "Production Individualization Agreement",
    type: "contractual",
    glossId: "aip",
  },
  {
    id: "cip",
    label: "CIP",
    label_en: "Production Individualization Commitment",
    type: "contractual",
    glossId: "cip",
  },
  {
    id: "primeiro-oleo",
    label: "Primeiro Óleo",
    label_en: "First Oil",
    type: "operational",
    glossId: "primeiro-oleo",
  },

  /* ANP regulatory test events */
  {
    id: "teste-formacao",
    label: "Teste de Formação",
    label_en: "Formation Test (TF/TFR/TFRE)",
    type: "contractual",
    glossId: "teste-formacao",
  },
  {
    id: "tld",
    label: "TLD",
    label_en: "Extended Well Test (EWT)",
    type: "contractual",
    glossId: "tld",
  },
  {
    id: "rftp",
    label: "RFTP",
    label_en: "Well Test Final Report",
    type: "instrument",
    glossId: "rftp",
  },
  {
    id: "i-engine",
    label: "i-Engine",
    label_en: "ANP i-Engine System",
    type: "instrument",
    glossId: "i-engine",
  },
  {
    id: "dpp",
    label: "DPP",
    label_en: "ANP Data Portal (DPP)",
    type: "instrument",
    glossId: "dpp",
  },
  {
    id: "bmp",
    label: "BMP",
    label_en: "Monthly Production Report",
    type: "instrument",
    glossId: "bmp",
  },

  /* geological */
  { id: "presal", label: "Pré-sal", label_en: "Pre-salt", type: "geological", glossId: "presal" },
  {
    id: "bacias-agrupadas",
    label: "Bacias Agrupadas",
    label_en: "Grouped Basins",
    type: "geological",
    glossId: "bacias-agrupadas",
  },
  {
    id: "ambiente",
    label: "Ambiente",
    label_en: "Environment",
    type: "geological",
    glossId: "ambiente",
  },

  /* equipment (curado a partir do siglário — siglas tier-1 do domínio) */
  {
    id: "bop",
    label: "BOP",
    label_en: "Blowout Preventer",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Preventor de erupção (Blowout Preventer). Conjunto de válvulas instalado na cabeça do poço durante a perfuração para conter pressão descontrolada e evitar blowout. Equipamento crítico de segurança.",
    fonte: "Siglário O&G / API",
  },
  {
    id: "fpso",
    label: "FPSO",
    label_en: "Floating Production, Storage and Offloading",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Unidade Flutuante de Produção, Estocagem e Transferência de Óleo. Navio adaptado que processa, armazena e transfere óleo produzido em campos offshore. Padrão dominante em águas profundas no Brasil.",
    fonte: "Siglário O&G",
  },
  {
    id: "anm-eq",
    label: "ANM",
    label_en: "Wet Christmas Tree (Árvore de Natal Molhada)",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Árvore de Natal Molhada — conjunto de válvulas e equipamentos de controle de fluxo instalado sobre a cabeça de um poço submarino. Permite produção, intervenção e segurança da poço subsea.",
    fonte: "Siglário O&G",
  },
  {
    id: "riser",
    label: "Riser",
    label_en: "Riser",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Tubulação que conecta o equipamento submarino (poço/ANM) à unidade flutuante de superfície (FPSO/sonda). Pode ser rígido (SCR), flexível ou híbrido (RHAS).",
    fonte: "Siglário O&G",
  },
  {
    id: "rov",
    label: "ROV",
    label_en: "Remotely Operated Vehicle",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Veículo Operado Remotamente. Robô submarino conectado por umbilical ao navio de apoio, usado para inspeção, intervenção e operação de equipamentos no leito marinho.",
    fonte: "Siglário O&G",
  },
  {
    id: "dhsv",
    label: "DHSV",
    label_en: "Downhole Safety Valve",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Válvula de Segurança de Subsuperfície (Downhole Safety Valve / SSSV / SCSSV). Instalada na coluna de produção dentro do poço; fecha automaticamente em caso de falha catastrófica na superfície.",
    fonte: "Siglário O&G",
  },
  {
    id: "bha",
    label: "BHA",
    label_en: "Bottom-Hole Assembly",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Composição de Fundo de Poço — porção inferior da coluna de perfuração que inclui broca, comandos, estabilizadores, motor de fundo e ferramentas de medição (MWD/LWD).",
    fonte: "Siglário O&G",
  },
  {
    id: "esp-eq",
    label: "ESP/BCS",
    label_en: "Electrical Submersible Pump",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Bomba Centrífuga Submersa elétrica. Método de elevação artificial em que uma bomba multi-estágio é instalada no fundo do poço para impulsionar fluidos à superfície.",
    fonte: "Siglário O&G",
  },
  {
    id: "mwd",
    label: "MWD",
    label_en: "Measure While Drilling",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Medição Durante a Perfuração. Conjunto de sensores no BHA que transmitem em tempo real dados direcionais (azimute, inclinação) e parâmetros operacionais durante a perfuração.",
    fonte: "Siglário O&G",
  },
  {
    id: "lwd",
    label: "LWD",
    label_en: "Logging While Drilling",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Perfilagem Durante a Perfuração. Sensores petrofísicos (raio gama, resistividade, densidade, neutron) integrados ao BHA que registram propriedades da formação enquanto se perfura.",
    fonte: "Siglário O&G",
  },
  {
    id: "manifold-submarino",
    label: "Manifold Submarino",
    label_en: "Subsea Manifold",
    type: "equipment",
    glossId: null,
    definicaoOverride:
      "Equipamento submarino de coleta/distribuição que agrega o fluxo de múltiplos poços para uma única linha que vai até a UEP, ou distribui injeção entre poços.",
    fonte: "Siglário O&G",
  },

  /* actor (atores adicionais do ecossistema regulatório/financeiro brasileiro) */
  {
    id: "ibama",
    label: "IBAMA",
    label_en: "Brazilian Institute of Environment",
    type: "actor",
    glossId: null,
    definicaoOverride:
      "Instituto Brasileiro do Meio Ambiente e dos Recursos Naturais Renováveis. Autarquia federal responsável pelo licenciamento ambiental de atividades de E&P offshore — atua em paralelo com a ANP no aspecto ambiental.",
    fonte: "Siglário O&G / Lei 7.735/1989",
  },
  {
    id: "conama",
    label: "CONAMA",
    label_en: "National Environmental Council",
    type: "actor",
    glossId: null,
    definicaoOverride:
      "Conselho Nacional do Meio Ambiente. Órgão consultivo e deliberativo do SISNAMA que estabelece normas e padrões ambientais aplicáveis à indústria de petróleo.",
    fonte: "Siglário O&G / Lei 6.938/1981",
  },
  {
    id: "ana-agencia",
    label: "ANA",
    label_en: "National Water Agency",
    type: "actor",
    glossId: null,
    definicaoOverride:
      "Agência Nacional de Águas e Saneamento Básico. Regula o uso de recursos hídricos em operações onshore (descarte, captação, água produzida).",
    fonte: "Siglário O&G",
  },
  {
    id: "ibp",
    label: "IBP",
    label_en: "Brazilian Petroleum Institute",
    type: "actor",
    glossId: null,
    definicaoOverride:
      "Instituto Brasileiro de Petróleo, Gás e Biocombustíveis. Associação de classe que representa operadoras e fornecedores; promove normas técnicas e diálogo regulatório.",
    fonte: "Siglário O&G",
  },
  {
    id: "bndes",
    label: "BNDES",
    label_en: "National Development Bank",
    type: "actor",
    glossId: null,
    definicaoOverride:
      "Banco Nacional de Desenvolvimento Econômico e Social. Financia projetos de E&P (FINEM, debêntures), conteúdo local e desenvolvimento da cadeia de fornecedores.",
    fonte: "Siglário O&G",
  },

  /* instrument (instrumentos contratuais e ambientais adicionais) */
  {
    id: "eia",
    label: "EIA",
    label_en: "Environmental Impact Study",
    type: "instrument",
    glossId: null,
    definicaoOverride:
      "Estudo de Impacto Ambiental. Documento técnico exigido pelo IBAMA para licenciamento de atividades com potencial degradador (perfuração offshore, sísmica, produção).",
    fonte: "Siglário O&G / Resolução CONAMA 1/1986",
  },
  {
    id: "rima",
    label: "RIMA",
    label_en: "Environmental Impact Report",
    type: "instrument",
    glossId: null,
    definicaoOverride:
      "Relatório de Impacto Ambiental. Síntese técnica do EIA em linguagem acessível, destinada à consulta pública no processo de licenciamento.",
    fonte: "Siglário O&G",
  },
  {
    id: "afe",
    label: "AFE",
    label_en: "Approval for Expenditure",
    type: "instrument",
    glossId: null,
    definicaoOverride:
      "Approval for Expenditure (Aprovação de Gastos / Autorização de Dispêndio). Mecanismo formal de aprovação prévia de gasto entre operadores e parceiros do consórcio antes de comprometer capital em poço ou instalação.",
    fonte: "Siglário O&G",
  },
  {
    id: "joa",
    label: "JOA",
    label_en: "Joint Operating Agreement",
    type: "instrument",
    glossId: null,
    definicaoOverride:
      "Joint Operating Agreement (Acordo de Operações Conjuntas). Acordo entre os consorciados de um Contrato de E&P que rege governança, votação, distribuição de custos e operação cotidiana do bloco.",
    fonte: "Siglário O&G",
  },
  {
    id: "epc",
    label: "EPC",
    label_en: "Engineering, Procurement, Construction",
    type: "instrument",
    glossId: null,
    definicaoOverride:
      "Engineering, Procurement and Construction (Engenharia, Suprimento, Construção e Montagem). Modalidade contratual em que um único contratado executa engenharia, compra de materiais e construção de uma instalação (FPSO, plataforma, gasoduto).",
    fonte: "Siglário O&G",
  },
];

const EDGES = [
  {
    source: "poco",
    target: "bloco",
    relation: "drilled_in",
    relation_label: "perfurado em",
    style: "solid",
  },
  {
    source: "poco",
    target: "ambiente",
    relation: "classified_by",
    relation_label: "classificado por",
    style: "dashed",
  },
  {
    source: "poco",
    target: "teste-formacao",
    relation: "undergoes",
    relation_label: "realiza",
    style: "solid",
  },
  {
    source: "poco",
    target: "tld",
    relation: "undergoes",
    relation_label: "realiza",
    style: "solid",
  },
  {
    source: "poco",
    target: "bacia-sedimentar",
    relation: "located_in",
    relation_label: "localizado em",
    style: "solid",
  },
  {
    source: "poco",
    target: "operador",
    relation: "operated_by",
    relation_label: "operado por",
    style: "solid",
  },
  {
    source: "poco",
    target: "notificacao-descoberta",
    relation: "may_register",
    relation_label: "pode registrar",
    style: "dashed",
  },
  {
    source: "poco",
    target: "presal",
    relation: "may_reach",
    relation_label: "pode atingir",
    style: "dashed",
  },
  {
    source: "poco",
    target: "formacao",
    relation: "traverses",
    relation_label: "atravessa",
    style: "dashed",
  },

  {
    source: "bloco",
    target: "bacia-sedimentar",
    relation: "delimited_in",
    relation_label: "delimitado em",
    style: "solid",
  },
  {
    source: "bloco",
    target: "contrato-ep",
    relation: "governed_by",
    relation_label: "regido por",
    style: "solid",
  },
  {
    source: "bloco",
    target: "operador",
    relation: "operated_by",
    relation_label: "operado por",
    style: "solid",
  },
  {
    source: "bloco",
    target: "pad",
    relation: "may_have",
    relation_label: "pode ter",
    style: "dashed",
  },
  {
    source: "bloco",
    target: "rodada-licitacao",
    relation: "originated_in",
    relation_label: "originado em",
    style: "solid",
  },
  {
    source: "bloco",
    target: "ambiente",
    relation: "classified_by",
    relation_label: "classificado por",
    style: "dashed",
  },

  {
    source: "contrato-ep",
    target: "anp",
    relation: "signed_with",
    relation_label: "celebrado com",
    style: "solid",
  },
  {
    source: "contrato-ep",
    target: "regime-contratual",
    relation: "defines",
    relation_label: "define",
    style: "solid",
  },
  {
    source: "contrato-ep",
    target: "periodo-exploratorio",
    relation: "organized_in",
    relation_label: "organizado em",
    style: "solid",
  },
  {
    source: "contrato-ep",
    target: "uts",
    relation: "measured_via",
    relation_label: "mede via",
    style: "solid",
  },

  /* ANP regulatory test event chain */
  {
    source: "teste-formacao",
    target: "amostra-fluido",
    relation: "yields",
    relation_label: "gera amostra de",
    style: "solid",
  },
  {
    source: "tld",
    target: "amostra-fluido",
    relation: "yields",
    relation_label: "gera amostra de",
    style: "solid",
  },
  {
    source: "teste-formacao",
    target: "rftp",
    relation: "requires_report",
    relation_label: "exige relatório",
    style: "solid",
  },
  {
    source: "tld",
    target: "rftp",
    relation: "requires_report",
    relation_label: "exige relatório",
    style: "solid",
  },
  {
    source: "tld",
    target: "i-engine",
    relation: "reported_via",
    relation_label: "reportado via",
    style: "solid",
  },
  { source: "tld", target: "bmp", relation: "generates", relation_label: "gera", style: "solid" },
  {
    source: "rftp",
    target: "dpp",
    relation: "submitted_via",
    relation_label: "enviado via",
    style: "solid",
  },
  {
    source: "anp",
    target: "i-engine",
    relation: "manages_via",
    relation_label: "gerencia via",
    style: "solid",
  },
  {
    source: "bmp",
    target: "anp",
    relation: "submitted_to",
    relation_label: "enviado à",
    style: "solid",
  },

  {
    source: "contrato-ep",
    target: "pem",
    relation: "requires",
    relation_label: "exige",
    style: "solid",
  },
  {
    source: "contrato-ep",
    target: "pte",
    relation: "monitored_via",
    relation_label: "acompanhado via",
    style: "solid",
  },
  {
    source: "pem",
    target: "uts",
    relation: "measured_in",
    relation_label: "medido em",
    style: "solid",
  },
  {
    source: "pem",
    target: "periodo-exploratorio",
    relation: "scoped_to",
    relation_label: "associado ao",
    style: "solid",
  },
  {
    source: "pte",
    target: "anp",
    relation: "submitted_to",
    relation_label: "enviado à",
    style: "solid",
  },
  {
    source: "pte",
    target: "dpp",
    relation: "submitted_via",
    relation_label: "enviado via",
    style: "solid",
  },

  {
    source: "pad",
    target: "bloco",
    relation: "evaluates",
    relation_label: "avalia",
    style: "solid",
  },
  {
    source: "pad",
    target: "rfad",
    relation: "closes_with",
    relation_label: "encerrado pelo",
    style: "solid",
  },
  {
    source: "rfad",
    target: "declaracao-comercialidade",
    relation: "may_yield",
    relation_label: "pode gerar",
    style: "dashed",
  },
  {
    source: "pad",
    target: "teste-formacao",
    relation: "may_include",
    relation_label: "pode incluir",
    style: "dashed",
  },
  { source: "pad", target: "tld", relation: "includes", relation_label: "inclui", style: "solid" },

  {
    source: "declaracao-comercialidade",
    target: "plano-desenvolvimento",
    relation: "requires",
    relation_label: "exige (180 dias)",
    style: "solid",
  },
  {
    source: "plano-desenvolvimento",
    target: "area-desenvolvimento",
    relation: "enables",
    relation_label: "habilita",
    style: "solid",
  },
  {
    source: "plano-desenvolvimento",
    target: "aip",
    relation: "accompanied_by",
    relation_label: "acompanhado por",
    style: "dashed",
  },
  {
    source: "plano-desenvolvimento",
    target: "cip",
    relation: "accompanied_by",
    relation_label: "acompanhado por",
    style: "dashed",
  },
  {
    source: "plano-desenvolvimento",
    target: "anp",
    relation: "approved_by",
    relation_label: "aprovado pela",
    style: "solid",
  },
  {
    source: "area-desenvolvimento",
    target: "primeiro-oleo",
    relation: "ends_with",
    relation_label: "encerrada pelo",
    style: "dashed",
  },
  {
    source: "primeiro-oleo",
    target: "campo",
    relation: "inaugurates",
    relation_label: "inaugura",
    style: "solid",
  },

  {
    source: "declaracao-comercialidade",
    target: "campo",
    relation: "originates",
    relation_label: "origina",
    style: "solid",
  },
  {
    source: "campo",
    target: "bacia-sedimentar",
    relation: "located_in",
    relation_label: "localizado em",
    style: "solid",
  },
  {
    source: "campo",
    target: "ambiente",
    relation: "classified_by",
    relation_label: "classificado por",
    style: "dashed",
  },
  {
    source: "campo",
    target: "reservatorio",
    relation: "sustained_by",
    relation_label: "sustentado por",
    style: "solid",
  },
  {
    source: "reservatorio",
    target: "bacia-sedimentar",
    relation: "contained_in",
    relation_label: "contido em",
    style: "solid",
  },
  {
    source: "reservatorio",
    target: "sistema-deposicional",
    relation: "characterized_by",
    relation_label: "caracterizado por",
    style: "solid",
  },
  {
    source: "reservatorio",
    target: "formacao",
    relation: "hosted_in",
    relation_label: "hospedado em",
    style: "solid",
  },

  {
    source: "operador",
    target: "processo-sancionador",
    relation: "may_have",
    relation_label: "pode ter",
    style: "dashed",
  },

  {
    source: "anp",
    target: "sigep",
    relation: "manages_via",
    relation_label: "gerencia via",
    style: "solid",
  },
  {
    source: "anp",
    target: "sep",
    relation: "oversees_via",
    relation_label: "fiscaliza via",
    style: "solid",
  },

  {
    source: "bacias-agrupadas",
    target: "bacia-sedimentar",
    relation: "classifies",
    relation_label: "classifica (ANP)",
    style: "dashed",
  },

  /* equipment → poço/campo */
  {
    source: "bop",
    target: "poco",
    relation: "installed_on",
    relation_label: "instalado em",
    style: "solid",
  },
  {
    source: "dhsv",
    target: "poco",
    relation: "installed_in",
    relation_label: "instalado em",
    style: "solid",
  },
  {
    source: "anm-eq",
    target: "poco",
    relation: "controls",
    relation_label: "controla",
    style: "solid",
  },
  {
    source: "bha",
    target: "poco",
    relation: "composes",
    relation_label: "compõe coluna",
    style: "dashed",
  },
  {
    source: "esp-eq",
    target: "poco",
    relation: "lifts_from",
    relation_label: "eleva fluido em",
    style: "dashed",
  },
  {
    source: "mwd",
    target: "poco",
    relation: "measures",
    relation_label: "mede em",
    style: "dashed",
  },
  { source: "lwd", target: "poco", relation: "logs", relation_label: "perfila", style: "dashed" },
  {
    source: "fpso",
    target: "campo",
    relation: "produces_at",
    relation_label: "produz em",
    style: "solid",
  },
  {
    source: "riser",
    target: "anm-eq",
    relation: "connects",
    relation_label: "conecta",
    style: "solid",
  },
  {
    source: "riser",
    target: "fpso",
    relation: "connects",
    relation_label: "conecta",
    style: "solid",
  },
  {
    source: "rov",
    target: "anm-eq",
    relation: "operates",
    relation_label: "opera",
    style: "dashed",
  },
  {
    source: "manifold-submarino",
    target: "poco",
    relation: "gathers_from",
    relation_label: "agrega fluxo de",
    style: "dashed",
  },
  {
    source: "manifold-submarino",
    target: "fpso",
    relation: "feeds",
    relation_label: "alimenta",
    style: "solid",
  },

  /* atores ambientais e financeiros */
  {
    source: "ibama",
    target: "operador",
    relation: "oversees_environment_of",
    relation_label: "fiscaliza ambientalmente",
    style: "solid",
  },
  { source: "ibama", target: "eia", relation: "requires", relation_label: "exige", style: "solid" },
  {
    source: "ibama",
    target: "rima",
    relation: "requires",
    relation_label: "exige",
    style: "solid",
  },
  {
    source: "conama",
    target: "ibama",
    relation: "guides",
    relation_label: "orienta normativamente",
    style: "solid",
  },
  {
    source: "ana-agencia",
    target: "operador",
    relation: "regulates_water_use_of",
    relation_label: "regula uso de água",
    style: "dashed",
  },
  {
    source: "ibp",
    target: "operador",
    relation: "represents",
    relation_label: "representa",
    style: "solid",
  },
  {
    source: "bndes",
    target: "bloco",
    relation: "finances",
    relation_label: "financia",
    style: "dashed",
  },

  /* instrumentos contratuais adicionais */
  {
    source: "afe",
    target: "poco",
    relation: "authorizes_spending_for",
    relation_label: "autoriza gasto em",
    style: "solid",
  },
  {
    source: "joa",
    target: "contrato-ep",
    relation: "complements",
    relation_label: "complementa",
    style: "solid",
  },
  {
    source: "epc",
    target: "fpso",
    relation: "delivers",
    relation_label: "entrega",
    style: "dashed",
  },
];

/* ─────────────────────────────────────────────────────────────
 * BUILDERS
 * ───────────────────────────────────────────────────────────── */

const NOW = new Date().toISOString();
const VERSION = "1.1.0";

function gloss(id) {
  return GLOSSARIO.find((t) => t.id === id);
}

function enrichTerm(t) {
  const align = alignmentFor(TERM_ALIGNMENT, t.id);
  const enrich = enrichmentFor(t.id);
  return {
    ...t,
    termo_en: enrich.termo_en,
    petrokgraph_uri: align.petrokgraph_uri,
    osdu_kind: align.osdu_kind,
    geocoverage: align.geocoverage,
    synonyms_pt: enrich.synonyms_pt,
    synonyms_en: enrich.synonyms_en,
    examples: enrich.examples,
  };
}

function buildGlossary() {
  const terms = [...GLOSSARIO.map(enrichTerm), ...OG_GLOSSARY, ...GPP_GLOSSARY];
  return {
    meta: { version: VERSION, generated: NOW, count: terms.length },
    terms,
  };
}

function buildExtendedTerms() {
  // Enrich each term with sweet_uri/sweet_alignment_type/sweet_module from the SWEET alignment file.
  const sweetMap = loadSweetAlignmentSync();
  const terms = EXTENDED_TERMS.map((t) => {
    const entries = sweetMap.get(t.id) || [];
    if (entries.length === 0) {
      return { ...t, sweet_uri: null, sweet_alignment_type: null, sweet_module: null };
    }
    // Use the first alignment entry for the primary sweet_uri fields on the term.
    const primary = entries[0];
    const uris = Array.isArray(primary.sweet_uris) ? primary.sweet_uris : [];
    return {
      ...t,
      sweet_uri: uris[0] || null,
      sweet_alignment_type: primary.alignment_type || null,
      sweet_module: primary.sweet_module || null,
    };
  });
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      count: terms.length,
      description:
        "Termos geológicos derivados de GeoCore/O3PO/GeoReservoir que o Geolytics usa mas não definia formalmente no glossário ANP.",
    },
    terms,
  };
}

function buildOntopetro() {
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      description: "Ontologia de Geociências de Petróleo — 6 módulos formais",
      sources: ["GeoCore", "PPDM", "GDGEO", "SPE-PRMS", "ANP", "OSDU"],
    },
    architecture: {
      layers: [
        { id: "camada1", name: "Foundational", desc: "Upper Ontology — UFO/BFO" },
        {
          id: "camada2",
          name: "Domain Ontology",
          desc: "Geociências de Petróleo (Geológico, Geofísico, Reservatório, Poços, Bacia)",
        },
        {
          id: "camada3",
          name: "Application Ontology",
          desc: "E&P Operacional — Exploração, Avaliação, Produção",
        },
      ],
    },
    classes: ONTOPETRO_CLASSES,
    properties: ONTOPETRO_PROPERTIES,
    relations: ONTOPETRO_RELATIONS,
    instances: ONTOPETRO_INSTANCES,
  };
}

function buildTaxonomies() {
  return {
    meta: { version: VERSION, generated: NOW, count: Object.keys(TAXONOMIES).length },
    taxonomies: TAXONOMIES,
  };
}

function buildModulesExtended() {
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      description:
        "Módulos analíticos internos Geolytics/Petrobras — apenas conteúdo público/conceitual",
      petrobras_namespace: "https://petrobras.com.br/geolytics/ontology/",
      modules: ["M7_geochem", "M8_rock", "M9_geomec", "M10_fluidos", "M-WellIntegrity"],
      publication_policy: "Apenas definições conceituais. Não inclui dados Sigilo=Interno.",
    },
    ...MODULES_EXTENDED,
  };
}

function buildPvtDictionary() {
  const high = PVT_FIELDS.filter((f) => f.completeness_pct >= 90).map((f) => f.name);
  const medium = PVT_FIELDS.filter((f) => f.completeness_pct >= 50 && f.completeness_pct < 90).map(
    (f) => f.name
  );
  const low = PVT_FIELDS.filter((f) => f.completeness_pct < 10).map((f) => f.name);
  return {
    meta: {
      source: "SIRR — Sistema Integrado de Reservatórios Petrobras",
      description: "Dicionário de campos PVT com completude real da base corporativa",
      total_fields: PVT_FIELDS.length,
      note: "Completude medida na base SIRR. Campos com < 10% são raridade analítica, não ausência de definição.",
    },
    fields: PVT_FIELDS,
    completeness_notes: {
      high_completeness: high,
      medium_completeness: medium,
      low_completeness_expected: low,
      rag_note:
        'Campos com baixa completude são dados de ensaios especiais — não indicam lacuna de dado, indicam raridade de análise. Um agente RAG deve interpretar "Fa Tanque disponível" como sinal de análise avançada.',
    },
  };
}

function buildSystems() {
  return {
    version: VERSION,
    generated: NOW,
    description: "Sistemas corporativos Petrobras que alimentam o GeoBrain",
    note: "Sistemas = proveniência, não acesso. Estes IDs são metadado de origem dos dados, não endpoints conectáveis.",
    systems: SYSTEMS,
  };
}

function buildRegisNer() {
  return {
    meta: {
      version: VERSION,
      source_corpus: "PetroGold",
      source_repo: "https://github.com/Petroles/regis-collection",
      source_paper: "Petroles / PUC-Rio — gold-standard NER corpus for Portuguese petroleum domain",
      description:
        "Mapeamento de tipos de entidade NER (PetroGold) para nós do entity-graph Geolytics. Use para NLP pipelines, fine-tuning de modelos e enriquecimento automático do dicionário.",
      relation_types_petro_re: REGIS_RELATION_TYPES,
      generated: NOW,
    },
    entity_mappings: REGIS_NER_MAPPINGS,
  };
}

function buildOntologyMap() {
  return {
    version: VERSION,
    generated: NOW,
    description:
      "Mapa das 5 camadas semânticas do domínio de O&G brasileiro. Use para entender a proveniência e o nível de formalidade de cada conceito.",
    layers: LAYER_DEFINITIONS,
    deduplication_rules: DEDUP_RULES,
    recommended_usage: RECOMMENDED_USAGE,
  };
}

function buildDatasets() {
  return {
    meta: { version: VERSION, generated: NOW, count: CONJUNTOS.length },
    datasets: CONJUNTOS,
  };
}

function buildOntologyTypes() {
  return {
    meta: { version: VERSION, generated: NOW },
    domains: DOMAINS,
    typology: ONTOLOGY_TYPES.tipologia,
    processing_levels: ONTOLOGY_TYPES.nivel,
  };
}

/* ─────────────────────────────────────────────────────────────
 * F5 — annotate `ontological_role` on every entity-graph node
 *
 * Implements the canonical role vocabulary from
 *   docs/ONTOLOGY_LAYERS.md §3 (six layers L1-L6) and §5 (auxiliary).
 *
 * Strategy: rule-based classifier with strict-first ordering. The first
 * matching rule wins. Manual overrides (a node already carrying an explicit
 * `ontological_role`) are respected and never reclassified.
 *
 * Canonical role values (see docs/ONTOLOGY_LAYERS.md):
 *   well_anchor, well_operation, artifact_primary, feature_observation,
 *   interpretation_process, engineering_artifact, regulatory_anchor,
 *   organizational_actor, domain_anchor, well_attribute_concept,
 *   equipment, governance_artifact, dataset_concept, lifecycle_state,
 *   lifecycle_outcome, kpi_metric, unclassified
 * ───────────────────────────────────────────────────────────── */

/**
 * Maps a node id with prefix `GEOMEC*` (Petrobras corporate L6 portfolio)
 * to its canonical ontological_role. Returns null if the id is not in scope.
 *
 * @param {string} id
 * @returns {string|null}
 */
function geomecCorporateRole(id) {
  // Pressões, gradientes, tensões — observable rock/well states (L4)
  const featureObservationIds = new Set([
    "GEOMEC001",
    "GEOMEC002",
    "GEOMEC005",
    "GEOMEC007",
    "GEOMEC008",
    "GEOMEC009",
    "GEOMEC010",
    "GEOMEC011",
    "GEOMEC012",
    "GEOMEC014",
    "GEOMEC016",
    "GEOMEC017",
    "GEOMEC018",
    "GEOMEC021",
    "GEOMEC024",
    // image-log feature pivots and per-feature sub-classes
    "GEOMEC023",
    "GEOMEC023A",
    "GEOMEC023B",
    "GEOMEC023C",
    "GEOMEC068",
    "GEOMEC069",
    "GEOMEC070",
    "GEOMEC071",
    "GEOMEC037",
    "GEOMEC038",
    "GEOMEC039",
    "GEOMEC040",
    "GEOMEC041",
    "GEOMEC042",
    "GEOMEC043",
    "GEOMEC053A",
    "GEOMEC053B",
    "GEOMEC044",
    "GEOMEC045",
    "GEOMEC077",
    "GEOMEC078",
    "GEOMEC079",
    "GEOMEC079A",
    "GEOMEC081",
    "GEOMEC082",
    "GEOMEC087",
    "GEOMEC075",
    "GEOMEC076",
    "GEOMEC_ROP_A",
  ]);
  if (featureObservationIds.has(id)) return "feature_observation";

  // Operações de poço / laboratório (L2)
  const wellOperationIds = new Set([
    "GEOMEC006", // LOT/xLOT/FIT (operação)
    "GEOMEC022", // Scratch test (lab op)
    "GEOMEC031",
    "GEOMEC032",
    "GEOMEC033",
    "GEOMEC034", // XLOT, AGP, Frac, DFIT
    "GEOMEC061",
    "GEOMEC062",
    "GEOMEC063",
    "GEOMEC064",
    "GEOMEC065",
    "GEOMEC066",
    "GEOMEC067", // ensaios laboratoriais
    "GEOMEC080", // sobrefuração com alívio de tensão
    "GEOMEC052B", // Setpoint MPD / SBP (operação)
  ]);
  if (wellOperationIds.has(id)) return "well_operation";

  // Engineering artifacts (L6)
  const engineeringArtifactIds = new Set([
    "GEOMEC019",
    "GEOMEC020", // ECD, MPD design
    "GEOMEC036", // Fórmula de ECD (design formula)
  ]);
  if (engineeringArtifactIds.has(id)) return "engineering_artifact";

  // Interpretation processes (L5)
  const interpretationProcessIds = new Set([
    "GEOMEC015", // Estabilidade de Poço / análise
    "GEOMEC035", // Modelo Geomecânico 3D (modelagem)
    "GEOMEC046", // Faixas de risco (classificação)
    "GEOMEC072", // Interpretação de perfil de imagem
    "GEOMEC083", // Inversão formal de mecanismos focais
    "GEOMEC085", // Estatística circular bimodal
    "GEOMEC086", // Inversão de slip de falha
    "GEOMEC027", // IMGR — índice de modelagem
  ]);
  if (interpretationProcessIds.has(id)) return "interpretation_process";

  // Software systems / databases / report repositories (dataset_concept)
  const datasetConceptIds = new Set([
    "GEOMEC025", // CSD — centro de suporte à decisão
    "GEOMEC028", // GeomecBR — simulador
    "GEOMEC029", // GERESIM
    "GEOMEC030", // SIGEO/SEST TR
    "GEOMEC047", // SIMCARR
    "GEOMEC051", // OpenWells/Atlas
    "GEOMEC074", // Geolog (software)
  ]);
  if (datasetConceptIds.has(id)) return "dataset_concept";

  // L3 artifact primary
  if (id === "GEOMEC073") return "artifact_primary"; // BOL — Borehole Oriented Log
  if (id === "GEOMEC048") return "artifact_primary"; // PWDa — pressure-while-drilling artifact

  // Equipment (physical hardware)
  if (id === "GEOMEC052A") return "equipment"; // PRV — pressure relief valve

  // Governance / quality scheme / report
  const governanceArtifactIds = new Set([
    "GEOMEC026A", // QPG — quadro de previsões
    "GEOMEC084", // Esquema de Qualidade WSM 2025
    "GEOMEC_ROP_B", // Relatório de operações de perfilagem
  ]);
  if (governanceArtifactIds.has(id)) return "governance_artifact";

  return null;
}

/**
 * Maps academic geomechanics ids (`GM*`) to their canonical role.
 * @param {string} id
 * @returns {string|null}
 */
function geomecAcademicRole(id) {
  // GM001-GM003 stress states; GM004 pore pressure; GM013-GM025 rock-mech
  // properties / classification metrics / regimes — all observable feature_observation.
  const featureObservationIds = new Set([
    "GM001",
    "GM002",
    "GM003",
    "GM004",
    "GM013",
    "GM014",
    "GM015",
    "GM016",
    "GM017",
    "GM018",
    "GM019",
    "GM020",
    "GM021",
    "GM022",
    "GM023",
    "GM024",
    "GM025",
  ]);
  if (featureObservationIds.has(id)) return "feature_observation";

  // GM005 mud window — engineering design output (L6)
  if (id === "GM005") return "engineering_artifact";

  // GM006 Mohr circle (graphical method); GM007-GM009 failure criteria;
  // GM010-GM012 MEM models — interpretation processes (L5)
  const interpretationProcessIds = new Set([
    "GM006",
    "GM007",
    "GM008",
    "GM009",
    "GM010",
    "GM011",
    "GM012",
  ]);
  if (interpretationProcessIds.has(id)) return "interpretation_process";

  // GM026 Wellbore-as-calibration-point — well anchor (L1)
  if (id === "GM026") return "well_anchor";

  // GM027 LaudoGeomecanico — engineering artifact / report
  if (id === "GM027") return "governance_artifact";

  return null;
}

/**
 * Maps fracture-pillar ids (`GF*`) — all are L4 features (feature_observation).
 * @param {string} id
 * @returns {string|null}
 */
function geomecFractureRole(id) {
  if (/^GF\d{3}$/.test(id)) return "feature_observation";
  return null;
}

/**
 * Maps `operational`-typed nodes by id.
 * @param {string} id
 * @returns {string|null}
 */
function operationalRole(id) {
  // L1 well anchors — physical/temporal anchors of the well
  const wellAnchorIds = new Set([
    "poco",
    "wellbore",
    "axon-term-furo",
    "axon-term-poco",
    "axon-term-poco-presal",
    "axon-term-poco-comprado",
    "axon-term-poco-nao-br",
  ]);
  if (wellAnchorIds.has(id)) return "well_anchor";

  // Spatial / contractual / regulatory anchors (regulatory_anchor)
  const regulatoryAnchorIds = new Set([
    "bloco",
    "campo",
    "bacia-sedimentar",
    "reservatorio",
    "play",
    "prospecto",
    "acumulacao",
    "primeiro-oleo",
  ]);
  if (regulatoryAnchorIds.has(id)) return "regulatory_anchor";

  // L2 well operations
  const wellOperationIds = new Set([
    "drilling-activity",
    "completacao",
    "operacoes-geologicas",
    "well-activity-program",
    "activity-plan",
  ]);
  if (wellOperationIds.has(id)) return "well_operation";

  // Plan/program templates and lifecycle/governance descriptors → governance_artifact
  const governanceArtifactIds = new Set([
    "activity-template",
    "well-activity-phase-type",
    "drilling-reason-type",
    "lessons-learned",
    "retro-analysis",
    "input-elaboration",
    "operational-monitoring",
    "formation-evaluation",
  ]);
  if (governanceArtifactIds.has(id)) return "governance_artifact";

  // 3W operational-typed nodes named `event_*` are observable production events
  if (/^event_/.test(id)) return "feature_observation";

  return null;
}

/**
 * Maps `analytical`-typed nodes by id. Disambiguates operations from artifacts
 * from interpretation outcomes per docs/ONTOLOGY_LAYERS.md §3.
 *
 * Borderline decisions:
 *  - wireline-logging / coring / mudlogging / etc. → well_operation (the
 *    operation/process; the artifact it produces is captured by adjacent
 *    `*-sample` / `mudlogging-time-series` / `formation-pressure-point` ids).
 *  - mudlogging-time-series → artifact_primary (the data series, not the op).
 *  - campo-tensional → feature_observation (the stress field state).
 *  - janela-lama → engineering_artifact (the operational window).
 *  - laudo-geomecanico / IGP / PAG / QPG → governance_artifact (reports).
 *
 * @param {string} id
 * @param {string} label
 * @returns {string|null}
 */
function analyticalRole(id, label) {
  // L1 well anchors (Axon Termo nodes naming the well concept itself).
  // These are typed `analytical` in the source but are the canonical
  // term entries for the Poço/Furo L1 anchor — see docs/ONTOLOGY_LAYERS.md §3.
  const wellAnchorIds = new Set([
    "axon-term-poco",
    "axon-term-furo",
    "axon-term-poco-presal",
    "axon-term-poco-comprado",
    "axon-term-poco-nao-br",
  ]);
  if (wellAnchorIds.has(id)) return "well_anchor";

  // L2 well operations (procedure-named)
  const wellOperationIds = new Set([
    "wireline-logging",
    "coring",
    "mudlogging",
    "cuttings-sampling",
    "sidewall-sampling",
    "formation-testing",
    "geostopping",
    "mwd-lwd",
    "wireline-run",
    "lwd-run",
    "core-run",
    "axon-asn-perfilagem",
    "axon-asn-testemunhagem",
    "axon-asn-mudlogging",
    "axon-asn-op-amostras-fluido",
    "axon-asn-op-amostras-rocha",
    "axon-asn-teste-formacao-aberto",
    "axon-asn-pressao-temperatura",
  ]);
  if (wellOperationIds.has(id)) return "well_operation";

  // L3 artefatos primários (Sample / WellLog / TestData)
  const artifactPrimaryIds = new Set([
    "testemunho",
    "perfil-poco",
    "core-sample",
    "core-plug",
    "sidewall-core-sample",
    "cuttings-sample-detailed",
    "fluid-sample",
    "amostra-fluido",
    "mudlogging-time-series",
    "formation-pressure-point",
    "dst-interval",
    "drilling-parameters",
    "axon-term-amostra",
    "axon-term-acervo-amostras",
    "axon-term-amostragem-calha-prevista",
  ]);
  if (artifactPrimaryIds.has(id)) return "artifact_primary";

  // L4 features (geological/geochemical observations & states)
  const featureObservationIds = new Set([
    "litologia",
    "facies-sedimentar",
    "topo-formacional",
    "trajetoria-poco",
    "materia-organica",
    "maturidade-termal",
    "biomarcador",
    "potencial-selante",
    "classe-fluido",
    "campo-tensional",
    "ocorrencia-geomec",
    "bottom-hole-pressure-type",
    "annular-fluid-type",
    "gas-show-event",
    "kick-event",
    "geostopping-event",
  ]);
  if (featureObservationIds.has(id)) return "feature_observation";

  // L5 interpretation processes
  const interpretationProcessIds = new Set([
    "modelo-petrofisico",
    "correlacao-oleo-rocha",
    "drx",
    "frx",
    "gc-ms",
    "sara",
    "pvt",
    "dna-geoquimico",
    "axon-asn-aval-final-poco",
    "axon-asn-planejamento",
    "axon-sub-prog-aquisicao",
  ]);
  if (interpretationProcessIds.has(id)) return "interpretation_process";

  // L6 engineering artifacts (operational design outputs)
  const engineeringArtifactIds = new Set(["janela-lama", "cementing-fluid"]);
  if (engineeringArtifactIds.has(id)) return "engineering_artifact";

  // Governance/lifecycle/state descriptors and well-attribute concepts
  if (id === "axon-asn-status-poco") return "governance_artifact";
  if (id === "axon-sub-dados-culturais") return "well_attribute_concept";

  // Lâmina d'água and classifications — controlled-vocab attributes (well_attribute_concept)
  const wellAttributeConceptIds = new Set([
    "axon-term-lamina-agua",
    "axon-term-lamina-agua-rasa",
    "axon-term-lamina-agua-profunda",
    "axon-term-lamina-agua-ultraprofunda",
    "axon-term-objetivo-poco",
    "axon-term-classificacao-poco",
  ]);
  if (wellAttributeConceptIds.has(id)) return "well_attribute_concept";

  // Axon term campo (Field) — a regulatory anchor in operational sense
  if (id === "axon-term-campo") return "regulatory_anchor";

  // IGP report — governance artifact
  if (id === "axon-term-igp") return "governance_artifact";

  return null;
}

/**
 * Maps `contractual`-typed nodes. Reports → governance_artifact;
 * test data → artifact_primary; lifecycle / regulatory obligations →
 * regulatory_anchor; service descriptions → well_operation.
 * @param {string} id
 * @returns {string|null}
 */
function contractualRole(id) {
  // L3 artifact primary (test data)
  const artifactPrimaryIds = new Set(["teste-formacao", "tld"]);
  if (artifactPrimaryIds.has(id)) return "artifact_primary";

  // Reports / programs / governance docs
  const governanceArtifactIds = new Set([
    "pem",
    "pte",
    "pad",
    "rfad",
    "aip",
    "cip",
    "roa",
    "pag",
    "frame",
    "ogeomec",
    "rcsd",
    "qpg",
    "bdp",
    "igp",
    "perfil-composto",
    "rmg",
    "laudo-geomecanico",
    "document-type",
    "acl",
    "plano-desenvolvimento",
    "declaracao-comercialidade",
  ]);
  if (governanceArtifactIds.has(id)) return "governance_artifact";

  // Regulatory / contractual anchors
  const regulatoryAnchorIds = new Set(["contrato-ep", "rodada-licitacao", "area-desenvolvimento"]);
  if (regulatoryAnchorIds.has(id)) return "regulatory_anchor";

  // KPI / metric concepts
  const wellAttributeConceptIds = new Set(["recurso", "reserva"]);
  if (wellAttributeConceptIds.has(id)) return "well_attribute_concept";

  return null;
}

/**
 * Maps `instrument`-typed nodes. Distinguishes regulatory systems,
 * databases/software (dataset_concept), regulatory anchors, and physical
 * sensor measurands (which become well_attribute_concept since they are
 * controlled-vocab measurand identifiers).
 * @param {string} id
 * @returns {string|null}
 */
function instrumentRole(id) {
  // Regulatory anchors / regulatory subsystems
  const regulatoryAnchorIds = new Set([
    "sigep",
    "sep",
    "uts",
    "regime-contratual",
    "periodo-exploratorio",
    "processo-sancionador",
    "notificacao-descoberta",
    "rftp",
    "i-engine",
    "dpp",
    "bmp",
    "eia",
    "rima",
    "afe",
    "joa",
    "epc",
  ]);
  if (regulatoryAnchorIds.has(id)) return "regulatory_anchor";

  // Database systems / software platforms / pipelines / repositories
  const datasetConceptIds = new Set([
    "sirr",
    "bdoc",
    "vge",
    "cassandra-exata-curva-tempo",
    "exata",
    "sigeo",
    "bdiep",
    "bdiap",
    "aida",
    "geodo",
    "gda",
  ]);
  if (datasetConceptIds.has(id)) return "dataset_concept";

  // Controlled-vocabulary attribute concepts
  const wellAttributeConceptIds = new Set(["unidade-medida", "log-curve-type"]);
  if (wellAttributeConceptIds.has(id)) return "well_attribute_concept";

  // Seismic acquisition/processing — well_operation (acquisition program)
  // and dataset_concept (processing project) respectively.
  if (id === "seismic-acquisition-survey") return "well_operation";
  if (id === "seismic-processing-project") return "interpretation_process";

  // Wellbore trajectory artifact — L3 primary
  if (id === "wellbore-trajectory") return "artifact_primary";

  // 3W sensor channels — measurand identifiers (well_attribute_concept).
  if (/^sensor_/.test(id)) return "well_attribute_concept";

  return null;
}

/**
 * Maps `equipment`-typed and `geological`-typed defaults.
 * @param {string} id
 * @returns {string|null}
 */
function equipmentRole(id) {
  // wellbore-architecture and casing-design are L6 engineering artifacts
  if (id === "wellbore-architecture" || id === "casing-design") {
    return "engineering_artifact";
  }
  if (id === "facility-type") return "well_attribute_concept";
  // axon-term-sonda → equipment (Sonda is the rig)
  return "equipment";
}

/**
 * Top-level rule-based role classifier. Returns a canonical `ontological_role`
 * value or `"unclassified"` if no rule applies.
 *
 * Order:
 *   1. Strict type-based rules (axon_domain, lifecycle_state, lifecycle_outcome,
 *      actor, regulatory_*, equipment, governance_*, portfolio_concept,
 *      project, decision_event)
 *   2. Geomechanics-specific id-prefixed rules
 *   3. Per-type id-based rules (operational, analytical, contractual,
 *      instrument, equipment)
 *   4. Type-default fallbacks (geological → feature_observation, etc.)
 *
 * @param {{id:string, type:string, label?:string, definition?:string}} node
 * @returns {string} canonical `ontological_role` (or `"unclassified"`)
 */
function inferOntologicalRole(node) {
  const id = node.id;
  const t = node.type;
  const label = node.label || "";

  // 1. Strict type-based rules
  if (t === "axon_domain") return "domain_anchor";
  if (t === "lifecycle_state") return "lifecycle_state";
  if (t === "lifecycle_outcome") return "lifecycle_outcome";
  if (t === "actor") return "organizational_actor";
  if (
    t === "regulatory_anchor" ||
    t === "regulatory_doc" ||
    t === "regulatory_event" ||
    t === "regulatory_obligation"
  ) {
    return "regulatory_anchor";
  }
  if (
    t === "governance_doc" ||
    t === "governance_committee" ||
    t === "governance_program" ||
    t === "portfolio_concept" ||
    t === "project" ||
    t === "decision_event"
  ) {
    return "governance_artifact";
  }

  // 2. Geomec-specific (id prefix)
  if (t === "geomec_corporate") {
    const r = geomecCorporateRole(id);
    if (r) return r;
  }
  if (t === "geomec_academic") {
    const r = geomecAcademicRole(id);
    if (r) return r;
  }
  if (t === "geomec_fracture") {
    const r = geomecFractureRole(id);
    if (r) return r;
  }

  // 3. Per-type id-based rules
  if (t === "operational") {
    const r = operationalRole(id);
    if (r) return r;
  }
  if (t === "analytical") {
    const r = analyticalRole(id, label);
    if (r) return r;
  }
  if (t === "contractual") {
    const r = contractualRole(id);
    if (r) return r;
  }
  if (t === "instrument") {
    const r = instrumentRole(id);
    if (r) return r;
  }
  if (t === "equipment") {
    return equipmentRole(id);
  }

  // 4. Type-default fallbacks
  if (t === "geological") return "feature_observation";

  return "unclassified";
}

/**
 * Final pass: writes `ontological_role` onto every node. Respects manual
 * overrides — nodes that already carry the field are not reclassified.
 * Mutates the array in place and returns the same reference.
 *
 * @param {Object[]} nodes
 * @returns {Object[]} same array, mutated
 */
function annotateOntologicalRoles(nodes) {
  for (const n of nodes) {
    if (typeof n.ontological_role === "string" && n.ontological_role.length > 0) {
      continue; // respect curator override
    }
    n.ontological_role = inferOntologicalRole(n);
  }
  return nodes;
}

/**
 * Builds the complete entity-graph JSON object by merging base ENTITY_NODES,
 * OntoPetro/M7-M10 nodes, OSDU Layer-4 nodes, OSDU extra nodes, and
 * OG (operacoes-geologicas) nodes. Each node is enriched with ontology
 * alignment (PetroKGraph, OSDU, GeoSciML), OSDU canonical definitions, SKOS
 * aliases, and synonyms/examples from the enrichment tables. Edges are
 * collected from all edge arrays and normalised with bilingual relation labels.
 *
 * @returns {{version: string, generated: string, source: string, nodes: Object[], edges: Object[]}}
 */
function buildEntityGraph() {
  const ext = (id) => EXTENDED_TERMS.find((t) => t.id === id);
  const baseNodes = ENTITY_NODES.map((n) => {
    const g = n.glossId ? gloss(n.glossId) : null;
    const e = n.extendedId ? ext(n.extendedId) : null;
    const align = alignmentFor(ENTITY_ALIGNMENT, n.id);
    const enrich = n.glossId
      ? enrichmentFor(n.glossId)
      : { synonyms_pt: [], synonyms_en: [], examples: [] };
    const canon = osduCanonical(align.osdu_kind);
    return {
      id: n.id,
      label: n.label,
      label_en: n.label_en,
      type: n.type,
      color: COLORS[n.type],
      size: SIZES[n.type],
      definition: n.definicaoOverride || (g ? g.definicao : e ? e.definicao : ""),
      definition_en_canonical: canon.definition_en_canonical,
      legal_source: n.fonte || (g ? g.fonte : e ? e.legal_source : null),
      ...(n.primary_key ? { primary_key: n.primary_key } : {}),
      ...(n.primary_key_standard ? { primary_key_standard: n.primary_key_standard } : {}),
      ...(n.primary_key_pattern ? { primary_key_pattern: n.primary_key_pattern } : {}),
      ...(n.joined_by_modules ? { joined_by_modules: n.joined_by_modules } : {}),
      datasets: g && Array.isArray(g.apareceEm) ? g.apareceEm : [],
      petrokgraph_uri: align.petrokgraph_uri,
      osdu_kind: align.osdu_kind,
      geosciml_uri: align.geosciml_uri,
      owl_uri: canon.owl_uri,
      geocoverage: align.geocoverage,
      synonyms_pt: e ? e.synonyms_pt : enrich.synonyms_pt,
      synonyms_en: e ? e.synonyms_en : enrich.synonyms_en,
      examples: e ? e.examples : enrich.examples,
      glossary_id: n.glossId || null,
      extended_id: n.extendedId || null,
    };
  });
  /* Ontopetro/M7-M10 nodes — alignment via ONTOPETRO_ALIGNMENT, com merge OSDU
     (incluindo as 25 classes OSDU extras vindas do osdu-extra-nodes.js). */
  const MERGED_ALIGNMENT = {
    ...ONTOPETRO_ALIGNMENT,
    ...OSDU_ALIGNMENT_ADDITIONS,
    ...OSDU_EXTRA_ALIGNMENT,
  };
  const ontopetroNodes = ONTOPETRO_NODES.map((n) => {
    const align = alignmentFor(MERGED_ALIGNMENT, n.id);
    const canon = osduCanonical(align.osdu_kind);
    return {
      id: n.id,
      label: n.label,
      label_en: n.label_en,
      type: n.type,
      color: COLORS[n.type],
      size: SIZES[n.type],
      definition: n.definition,
      definition_en_canonical: canon.definition_en_canonical,
      legal_source: n.fonte || null,
      datasets: [],
      petrokgraph_uri: align.petrokgraph_uri,
      osdu_kind: align.osdu_kind,
      geosciml_uri: align.geosciml_uri,
      owl_uri: canon.owl_uri,
      geocoverage: align.geocoverage,
      synonyms_pt: [],
      synonyms_en: [],
      examples: [],
      glossary_id: null,
      extended_id: null,
      ontopetro: true,
    };
  });
  /* OSDU layer-4 nodes (4 novos: wellbore, topo-formacional, trajetoria-poco, unidade-medida) */
  const osduNodes = OSDU_NODES.map((n) => {
    const align = alignmentFor(MERGED_ALIGNMENT, n.id);
    const kind = n.osdu_kind_override || align.osdu_kind;
    const canon = osduCanonical(kind);
    return {
      id: n.id,
      label: n.label,
      label_en: n.label_en,
      type: n.type,
      color: COLORS[n.type],
      size: n.size || SIZES[n.type],
      definition: n.definition,
      definition_en_canonical: canon.definition_en_canonical,
      legal_source: n.fonte || null,
      datasets: n.datasets || [],
      petrokgraph_uri: align.petrokgraph_uri,
      osdu_kind: kind,
      geosciml_uri: align.geosciml_uri,
      owl_uri: canon.owl_uri,
      geocoverage: n.layers_override || align.geocoverage,
      synonyms_pt: n.synonyms_pt || [],
      synonyms_en: n.synonyms_en || [],
      examples: n.examples || [],
      glossary_id: null,
      extended_id: null,
      osdu: true,
    };
  });
  /* OSDU extra nodes (25 classes derived from Accenture OSDU.ttl) */
  const osduExtraNodes = OSDU_EXTRA_NODES.map((n) => {
    const align = alignmentFor(MERGED_ALIGNMENT, n.id);
    const kind = n.osdu_kind_override || align.osdu_kind;
    const canon = osduCanonical(kind);
    return {
      id: n.id,
      label: n.label,
      label_en: n.label_en,
      type: n.type,
      color: COLORS[n.type],
      size: n.size || SIZES[n.type] || 16,
      definition: n.definition,
      definition_en_canonical: canon.definition_en_canonical,
      legal_source: n.fonte || null,
      datasets: n.datasets || [],
      petrokgraph_uri: align.petrokgraph_uri,
      osdu_kind: kind,
      geosciml_uri: align.geosciml_uri,
      owl_uri: canon.owl_uri,
      geocoverage: n.layers_override || align.geocoverage,
      synonyms_pt: n.synonyms_pt || [],
      synonyms_en: n.synonyms_en || [],
      examples: n.examples || [],
      glossary_id: null,
      extended_id: null,
      osdu_extra: true,
    };
  });
  /* Final nodes carry their SKOS aliases for direct interop. */
  const nodes = [
    ...[...baseNodes, ...ontopetroNodes, ...osduNodes, ...osduExtraNodes].map(withSkosAliases),
    /* OG nodes are stored fully-baked (skos aliases inlined where appropriate) and
       are NOT re-mapped through withSkosAliases — that would add empty aliases to
       the 30 OG nodes that intentionally do not carry them.
       Geocoverage fallback: if an OG node has no geocoverage field, look it up from
       ENTITY_ALIGNMENT so all nodes have at least one layer tag. */
    ...OG_NODES.map((n) => {
      if (n.geocoverage && n.geocoverage.length) return n;
      const align = alignmentFor(ENTITY_ALIGNMENT, n.id);
      return align.geocoverage.length ? { ...n, geocoverage: align.geocoverage } : n;
    }),
    /* GPP nodes: 27 governance/portfolio/lifecycle nodes — fully-baked, skos fields inlined.
       Same geocoverage-fallback policy as OG. */
    ...GPP_NODES.map((n) => {
      if (n.geocoverage && n.geocoverage.length) return n;
      const align = alignmentFor(ENTITY_ALIGNMENT, n.id);
      return align.geocoverage.length ? { ...n, geocoverage: align.geocoverage } : n;
    }),
    /* 3W nodes: 27 sensors + 10 events + 14 equipment — fully-baked, skos fields inlined */
    ...THREEW_VARIABLES,
    ...THREEW_EVENTS,
    ...THREEW_EQUIPMENT,
  ];
  /* Apply 3W equipment patches (enriches existing nodes like dhsv in-place) */
  for (const patch of THREEW_EQUIPMENT_PATCHES) {
    const idx = nodes.findIndex((n) => n.id === patch.id);
    if (idx !== -1) Object.assign(nodes[idx], patch);
  }
  /* Apply GPP patches (enriches existing pem/pad/contrato-ep/declaracao-comercialidade
     in-place with module ref + ANP/PROPEX evidence_refs + GPP role flag). */
  for (const patch of GPP_NODE_PATCHES) {
    const idx = nodes.findIndex((n) => n.id === patch.id);
    if (idx !== -1) Object.assign(nodes[idx], patch);
  }
  /* deriva relation_label_en a partir do snake_case do campo relation, exceto
     quando a aresta já traz relation_label_en explícito (caso OG_EDGES, onde
     os labels foram traduzidos manualmente). */
  const edges = [
    ...EDGES,
    ...ONTOPETRO_EDGES,
    ...OSDU_EDGES,
    ...OSDU_EXTRA_EDGES,
    ...OG_EDGES,
    ...GPP_EDGES,
    ...THREEW_EDGES,
  ].map((e) => ({
    source: e.source,
    target: e.target,
    relation: e.relation,
    relation_label_pt: e.relation_label,
    relation_label_en: e.relation_label_en || e.relation.replace(/_/g, " "),
    style: e.style,
  }));

  /* L6 corporate Petrobras geomechanics — 92 entities (GEOMEC*) including
     DFIT, Breakout/Ovalização, BOL, Geolog, AZIE, HAZI, etc. Adds nodes and
     intra-corporate edges to the entity-graph so GraphRAG agents and
     Neo4j visualizations can resolve these concepts directly.
     F4: 6 deprecated duplicates are filtered here and their edges re-routed
     to surviving ids (bdp / bdiep / janela-lama / campo-tensional /
     laudo-geomecanico / GM017). Provenance preserved via source_reference
     applied to surviving nodes below. */
  const corpGraph = buildGeomecCorporateGraph(new Set(nodes.map((n) => n.id)));
  nodes.push(...corpGraph.nodes);
  edges.push(...corpGraph.edges);

  /* L1-L2 academic backbone (Fjaer/Zoback/ISRM, 27 GM* classes) + Pillar 4
     fracture branch (17 GF* classes). Adds the foundational geomechanics
     vocabulary plus bridge edges that:
       - merge the L6 corporate island into the main component via
         is_specialization_of / observed_in / produces;
       - tie the academic classes to operational pivots (poco,
         wireline-logging, core-sample, formation-testing, mwd-lwd, lwd, mwd,
         bdp, janela-lama, campo-tensional, laudo-geomecanico). */
  const acadGraph = buildGeomecAcademicGraph(new Set(nodes.map((n) => n.id)));
  nodes.push(...acadGraph.nodes);
  edges.push(...acadGraph.edges);

  /* F4 — apply source_reference cards onto each surviving node so the merged
     Petrobras corporate provenance (deprecated id, original definition,
     owner_department, internal_standards, sources) is visible to GraphRAG
     agents and crosswalk consumers without polluting the canonical
     definition field. Run AFTER the academic graph push so survivors that
     live in the academic module (e.g. GM017 Biot coefficient) are reachable. */
  for (const [survivorId, refs] of corpGraph.sourceReferences.entries()) {
    const idx = nodes.findIndex((n) => n.id === survivorId);
    if (idx === -1) continue;
    const existing = Array.isArray(nodes[idx].source_reference) ? nodes[idx].source_reference : [];
    nodes[idx].source_reference = existing.concat(refs);
  }

  /* F3 — Axon Petrobras Exploração glossary (data/axon-petrobras-glossary.json).
     Adds the 4-level Domínio → Assunto → Subassunto → Termo hierarchy as a
     sub-graph of `axon_domain`-typed Domínios plus analytical/equipment/
     geological Assuntos and Termos, then bridges:
       - Existing operations specialize the matching Axon Assunto
         (wireline-logging → Operação de Perfilagem, etc.).
       - Existing sample artifacts specialize axon-term-amostra.
       - Geomec L6 corporate + L1-L2 academic anchor on Domínio Geomecânica.
       - Existing igp / campo / poco / presal / ambiente nodes are enriched
         (not duplicated) by linking the Axon term node via
         is_specialization_of and is_part_of.
       - Format-only well attributes (Sigla, DATUM, MC, Sidetrack, coords...)
         are NOT emitted as nodes; they live in data/well-attributes.json. */
  const axonGraph = buildAxonGlossaryGraph(new Set(nodes.map((n) => n.id)));
  nodes.push(...axonGraph.nodes);
  edges.push(...axonGraph.edges);

  /* F4 — wire the four remaining isolated GEOMEC nodes (046, 076, 086, 087)
     into the giant component as a case-test of the 6-layer ontology model
     (Q6/option 2). Uses only canonical predicates; runs last so all candidate
     target ids (axon-dom-geomecanica, falha, GM010-12, GEOMEC0**) are in scope. */
  const isolatedBridges = buildIsolatedGeomecBridges(new Set(nodes.map((n) => n.id)));
  edges.push(...isolatedBridges.edges);

  /* F5 — annotate `ontological_role` on every node using the rule-based
     classifier defined above. Final pass so all merge sources (base +
     ontopetro + osdu + 3W + GEOMEC corporate + academic + Axon glossary +
     OG + GPP + isolated bridges) are in scope. Manual overrides on individual
     nodes are respected. See docs/ONTOLOGY_LAYERS.md §3 + §5. */
  annotateOntologicalRoles(nodes);

  return {
    version: VERSION,
    generated: NOW,
    source:
      "Geolytics / ANP-SEP / SIGEP / GeoCore / O3PO / Petro KGraph / OSDU / Petrobras 3W / Geomec L6 Corporate / Geomec L1-L2 Academic + Fracture / Axon Petrobras Exploração",
    nodes,
    edges,
  };
}

function buildFull() {
  const ac = loadAcronyms();
  const graph = buildEntityGraph();
  const gso = loadGsoModules();
  const gsoTotal = gso.reduce((n, m) => n + (m.meta?.class_count || 0), 0);
  const seismic = buildSeismicConsolidated();
  const gm = loadGeomechanics();
  const gmf = loadGeomechanicsFractures();
  const ftg = loadFractureToGso();
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      description: "GeoBrain — complete merged dataset",
      counts: {
        glossary_terms: GLOSSARIO.length + OG_GLOSSARY.length + GPP_GLOSSARY.length,
        extended_terms: EXTENDED_TERMS.length,
        total_terms:
          GLOSSARIO.length + OG_GLOSSARY.length + GPP_GLOSSARY.length + EXTENDED_TERMS.length,
        datasets: CONJUNTOS.length,
        entity_nodes:
          ENTITY_NODES.length +
          ONTOPETRO_NODES.length +
          OSDU_NODES.length +
          OSDU_EXTRA_NODES.length +
          OG_NODES.length +
          GPP_NODES.length +
          THREEW_VARIABLES.length +
          THREEW_EVENTS.length +
          THREEW_EQUIPMENT.length,
        entity_edges:
          EDGES.length +
          ONTOPETRO_EDGES.length +
          OSDU_EDGES.length +
          OSDU_EXTRA_EDGES.length +
          OG_EDGES.length +
          GPP_EDGES.length +
          THREEW_EDGES.length,
        domains: DOMAINS.length,
        ontology_layers: LAYER_DEFINITIONS.length,
        ontopetro_classes: ONTOPETRO_CLASSES.length,
        ontopetro_properties: ONTOPETRO_PROPERTIES.length,
        ontopetro_relations: ONTOPETRO_RELATIONS.length,
        ontopetro_instances: ONTOPETRO_INSTANCES.length,
        modules_extended: Object.keys(MODULES_EXTENDED).length,
        pvt_fields: PVT_FIELDS.length,
        systems: SYSTEMS.length,
        regis_ner_mappings: REGIS_NER_MAPPINGS.length,
        ambiguity_alerts: AMBIGUITY_ALERTS.length,
        acronyms: ac ? ac.acronyms.length : 0,
        gso_modules: gso.length,
        gso_classes: gsoTotal,
        seismic_classes: seismic.meta.class_count,
        seismic_properties: seismic.meta.property_count,
        seismic_relations: seismic.meta.relation_count,
        seismic_instances: seismic.meta.instance_count,
        geomechanics_classes: gm ? (gm.classes || []).length : 0,
        geomechanics_properties: gm ? (gm.properties || []).length : 0,
        geomechanics_relations: gm ? (gm.relations || []).length : 0,
        geomechanics_instances: gm ? (gm.instances || []).length : 0,
        fracture_classes: gmf ? (gmf.classes || []).length : 0,
        fracture_to_gso_mappings: ftg ? (ftg.mappings || []).length : 0,
      },
      sources: [
        "ANP/SEP",
        "Lei 9478/1997",
        "GeoCore (UFRGS)",
        "Petro KGraph (PUC-Rio)",
        "O3PO (UFRGS)",
        "OSDU",
        "Petrobras/Geolytics internal (Layer 6)",
        "GSO/Loop3D (Layer 7, CC BY 4.0)",
        "Seismic (Yilmaz 2001, Russell 1988, Connolly 1999, Chopra & Marfurt 2007)",
        "Geomechanics (Fjaer et al. 2008, Zoback 2010, Hoek & Brown 2019, Anderson 1951)",
        "Petrobras 3W v2.0.0 (CC-BY 4.0, Vargas et al. 2019, DOI:10.1016/j.petrol.2019.106223)",
      ],
    },
    glossary: [...GLOSSARIO.map(enrichTerm), ...OG_GLOSSARY, ...GPP_GLOSSARY],
    extended_terms: EXTENDED_TERMS,
    entity_graph: graph,
    datasets: CONJUNTOS,
    ontology_types: {
      domains: DOMAINS,
      typology: ONTOLOGY_TYPES.tipologia,
      processing_levels: ONTOLOGY_TYPES.nivel,
    },
    ontology_map: buildOntologyMap(),
    ontopetro: buildOntopetro(),
    taxonomies: TAXONOMIES,
    modules_extended: MODULES_EXTENDED,
    pvt_dictionary: { fields: PVT_FIELDS, total: PVT_FIELDS.length },
    systems: SYSTEMS,
    regis_ner: { entity_mappings: REGIS_NER_MAPPINGS, relation_types: REGIS_RELATION_TYPES },
    acronyms: ac ? ac.acronyms : [],
    gso: gso.map((m) => ({
      module: m.meta.module,
      base_uri: m.meta.base_uri,
      class_count: m.meta.class_count,
      license: m.meta.license,
      attribution: m.meta.attribution,
      classes: m.classes,
    })),
    seismic: seismic,
    geomechanics: gm || null,
    geomechanics_fractures: gmf || null,
    fracture_to_gso_crosswalk: ftg || null,
  };
}

/* ─────────────────────────────────────────────────────────────
 * API v1
 * ───────────────────────────────────────────────────────────── */

const BASE_URL_PLACEHOLDER = "https://thiagoflc.github.io/geobrain";

/**
 * Builds the API index JSON object listing all public API and data file
 * endpoints for the GeoBrain deployment. Each endpoint is an absolute URL
 * formed from `BASE_URL_PLACEHOLDER`. Written to `api/v1/index.json`.
 *
 * @returns {{meta: {version: string, generated: string, base_url: string}, endpoints: Object.<string, string>}}
 */
function buildApiIndex() {
  return {
    meta: { version: VERSION, generated: NOW, base_url: BASE_URL_PLACEHOLDER },
    endpoints: {
      terms: `${BASE_URL_PLACEHOLDER}/api/v1/terms.json`,
      entities: `${BASE_URL_PLACEHOLDER}/api/v1/entities.json`,
      datasets: `${BASE_URL_PLACEHOLDER}/api/v1/datasets.json`,
      search_index: `${BASE_URL_PLACEHOLDER}/api/v1/search-index.json`,
      glossary: `${BASE_URL_PLACEHOLDER}/data/glossary.json`,
      extended_terms: `${BASE_URL_PLACEHOLDER}/data/extended-terms.json`,
      entity_graph: `${BASE_URL_PLACEHOLDER}/data/entity-graph.json`,
      ontology: `${BASE_URL_PLACEHOLDER}/data/ontology-types.json`,
      ontology_map: `${BASE_URL_PLACEHOLDER}/ai/ontology-map.json`,
      ontopetro: `${BASE_URL_PLACEHOLDER}/data/ontopetro.json`,
      osdu_mapping: `${BASE_URL_PLACEHOLDER}/data/osdu-mapping.json`,
      geolytics_ttl: `${BASE_URL_PLACEHOLDER}/data/geobrain.ttl`,
      webvowl_view: `https://service.tib.eu/webvowl/#iri=${BASE_URL_PLACEHOLDER}/data/geobrain.ttl`,
      cards_view: `${BASE_URL_PLACEHOLDER}/index-cards.html`,
      gso_cards_view: `${BASE_URL_PLACEHOLDER}/gso-cards.html`,
      gso_crosswalk: `${BASE_URL_PLACEHOLDER}/data/osdu-gso-crosswalk.json`,
      gso_faults: `${BASE_URL_PLACEHOLDER}/data/gso-faults.json`,
      gso_folds: `${BASE_URL_PLACEHOLDER}/data/gso-folds.json`,
      gso_foliations: `${BASE_URL_PLACEHOLDER}/data/gso-foliations.json`,
      gso_lineations: `${BASE_URL_PLACEHOLDER}/data/gso-lineations.json`,
      gso_contacts: `${BASE_URL_PLACEHOLDER}/data/gso-contacts.json`,
      taxonomies: `${BASE_URL_PLACEHOLDER}/data/taxonomies.json`,
      modules_extended: `${BASE_URL_PLACEHOLDER}/data/modules-extended.json`,
      pvt_dictionary: `${BASE_URL_PLACEHOLDER}/data/pvt-dictionary.json`,
      systems: `${BASE_URL_PLACEHOLDER}/data/systems.json`,
      regis_ner: `${BASE_URL_PLACEHOLDER}/data/regis-ner-schema.json`,
      acronyms: `${BASE_URL_PLACEHOLDER}/data/acronyms.json`,
      acronyms_api: `${BASE_URL_PLACEHOLDER}/api/v1/acronyms.json`,
      cgi_lithology: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-lithology.json`,
      cgi_osdu_lithology_map: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-osdu-lithology-map.json`,
      cgi_geologic_time: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-geologic-time.json`,
      cgi_fault_type: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-fault-type.json`,
      cgi_deformation_style: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-deformation-style.json`,
      cgi_contact_type: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-contact-type.json`,
      cgi_stratigraphic_rank: `${BASE_URL_PLACEHOLDER}/api/v1/cgi-stratigraphic-rank.json`,
      gwml2: `${BASE_URL_PLACEHOLDER}/api/v1/gwml2.json`,
      layer1_layer1b_equivalence: `${BASE_URL_PLACEHOLDER}/api/v1/layer1-layer1b-equivalence.json`,
      gsmlbh_properties: `${BASE_URL_PLACEHOLDER}/api/v1/gsmlbh-properties.json`,
      geomechanics: `${BASE_URL_PLACEHOLDER}/api/v1/geomechanics.json`,
      geomechanics_data: `${BASE_URL_PLACEHOLDER}/data/geomechanics.json`,
      geomechanics_fractures: `${BASE_URL_PLACEHOLDER}/data/geomechanics-fractures.json`,
      fracture_to_gso: `${BASE_URL_PLACEHOLDER}/data/fracture_to_gso.json`,
      full: `${BASE_URL_PLACEHOLDER}/data/full.json`,
      seismic: `${BASE_URL_PLACEHOLDER}/api/v1/seismic.json`,
      rag_corpus: `${BASE_URL_PLACEHOLDER}/ai/rag-corpus.jsonl`,
      system_prompt_pt: `${BASE_URL_PLACEHOLDER}/ai/system-prompt-ptbr.md`,
      system_prompt_en: `${BASE_URL_PLACEHOLDER}/ai/system-prompt-en.md`,
    },
  };
}

function buildApiAcronyms() {
  const ac = loadAcronyms();
  if (!ac) return { meta: { version: VERSION, generated: NOW, count: 0 }, acronyms: [] };
  return {
    meta: {
      version: VERSION,
      generated: NOW,
      count: ac.acronyms.length,
      by_category: ac.meta.by_category,
      excluded_from_rag: ac.acronyms.filter((a) => a.it_generic).length,
    },
    acronyms: ac.acronyms,
  };
}

function buildApiTerms() {
  const all = [
    ...GLOSSARIO.map((t) => {
      const enr = enrichmentFor(t.id);
      const align = alignmentFor(TERM_ALIGNMENT, t.id);
      return {
        id: t.id,
        termo: t.termo,
        termo_en: enr.termo_en,
        categoria: t.categoria,
        definicao: t.definicao,
        fonte: t.fonte,
        datasets: t.apareceEm,
        petrokgraph_uri: align.petrokgraph_uri,
        osdu_kind: align.osdu_kind,
        geocoverage: align.geocoverage,
        synonyms_pt: enr.synonyms_pt,
        synonyms_en: enr.synonyms_en,
        examples: enr.examples,
        source: "glossary",
      };
    }),
    ...EXTENDED_TERMS.map((t) => ({
      ...t,
      datasets: t.apareceEm,
      fonte: t.legal_source,
      source: "extended",
    })),
  ];
  return { meta: { version: VERSION, generated: NOW, count: all.length }, terms: all };
}

function buildApiEntities() {
  const graph = buildEntityGraph();
  const inEdges = (id) =>
    graph.edges
      .filter((e) => e.target === id)
      .map((e) => ({
        from: e.source,
        relation: e.relation,
        label: e.relation_label,
        style: e.style,
      }));
  const outEdges = (id) =>
    graph.edges
      .filter((e) => e.source === id)
      .map((e) => ({
        to: e.target,
        relation: e.relation,
        label: e.relation_label,
        style: e.style,
      }));
  return {
    meta: { version: VERSION, generated: NOW, count: graph.nodes.length },
    entities: graph.nodes.map((n) => ({
      ...n,
      relations: { outgoing: outEdges(n.id), incoming: inEdges(n.id) },
    })),
  };
}

function buildApiDatasets() {
  return {
    meta: { version: VERSION, generated: NOW, count: CONJUNTOS.length },
    datasets: CONJUNTOS.map((c) => ({
      id: c.id,
      titulo: c.titulo,
      descricao: c.descricao,
      fonte: c.fonte,
      formato: c.formato,
      frequencia: c.frequencia,
      contato: c.contato,
      colunas: c.colunas,
      terms_referenced: GLOSSARIO.filter(
        (t) => Array.isArray(t.apareceEm) && t.apareceEm.includes(c.id)
      ).map((t) => t.id),
    })),
  };
}

function tokenize(s) {
  return (s || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9 ]+/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 2);
}

/**
 * Builds a client-side full-text search index covering glossary terms,
 * datasets, and entity-graph nodes. Each item carries a pre-tokenised
 * `tokens` array (normalised, accent-stripped, deduplicated) for offline
 * token-match search in the browser. Written to `api/v1/search-index.json`.
 *
 * @returns {{meta: {version: string, generated: string, count: number}, items: Array<{id: string, type: string, title: string, text: string, tokens: string[]}>}}
 */
function buildSearchIndex() {
  const items = [];
  for (const t of GLOSSARIO) {
    items.push({
      id: `term:${t.id}`,
      type: "term",
      title: t.termo,
      text: `${t.termo}. ${t.definicao} Fonte: ${t.fonte}.`,
      tokens: Array.from(new Set(tokenize(`${t.termo} ${t.definicao} ${t.fonte}`))),
    });
  }
  for (const c of CONJUNTOS) {
    items.push({
      id: `dataset:${c.id}`,
      type: "dataset",
      title: c.titulo,
      text: `${c.titulo}. ${c.descricao} Fonte: ${c.fonte}.`,
      tokens: Array.from(new Set(tokenize(`${c.titulo} ${c.descricao} ${c.fonte}`))),
    });
  }
  for (const n of buildEntityGraph().nodes) {
    items.push({
      id: `entity:${n.id}`,
      type: "entity",
      title: n.label,
      text: `${n.label} (${n.label_en}). ${n.definition}`,
      tokens: Array.from(
        new Set(
          tokenize(
            `${n.label} ${n.label_en} ${n.definition} ${(n.synonyms_pt || []).join(" ")} ${(n.synonyms_en || []).join(" ")}`
          )
        )
      ),
    });
  }
  /* OSDU mapping reference */
  items.push({
    id: "dataset:osdu-mapping",
    type: "dataset",
    title: "OSDU Kind Mapping Table",
    text: "OSDU kind mapping with master/reference/wpc tripartition, Well/Wellbore disambiguation and ANP→OSDU lineage.",
    tokens: Array.from(
      new Set(
        tokenize(
          "OSDU kind mapping master-data reference-data work-product-component Well Wellbore Field Basin tripartição ANP"
        )
      )
    ),
  });

  // CGI Simple Lithology
  const cgiLithPath = path.join(ROOT, "data", "cgi-lithology.json");
  if (fs.existsSync(cgiLithPath)) {
    const lithData = JSON.parse(fs.readFileSync(cgiLithPath, "utf8"));
    const concepts =
      lithData.concepts || (Array.isArray(lithData) ? lithData.filter((x) => x.id) : []);
    for (const c of concepts) {
      items.push({
        id: `cgi-lith:${c.id}`,
        type: "lithology",
        title: c.label_pt || c.label_en || c.id,
        title_en: c.label_en,
        text: [c.label_pt, c.label_en, c.definition_en].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([c.label_pt, c.label_en, c.id, c.definition_en].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  // CGI Geologic Time
  const cgiTimePath = path.join(ROOT, "data", "cgi-geologic-time.json");
  if (fs.existsSync(cgiTimePath)) {
    const timeData = JSON.parse(fs.readFileSync(cgiTimePath, "utf8"));
    const units = timeData.units || (Array.isArray(timeData) ? timeData.filter((x) => x.id) : []);
    for (const u of units) {
      items.push({
        id: `cgi-time:${u.id}`,
        type: "geologic_time",
        title: u.label_pt || u.label_en || u.id,
        title_en: u.label_en,
        text: [u.label_pt, u.label_en, u.rank, u.brazil_notes].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([u.label_pt, u.label_en, u.id, u.rank, u.brazil_notes].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  // CGI Fault Type
  const cgiFaultPath = path.join(ROOT, "data", "cgi-fault-type.json");
  if (fs.existsSync(cgiFaultPath)) {
    const faultData = JSON.parse(fs.readFileSync(cgiFaultPath, "utf8"));
    const concepts =
      faultData.concepts || (Array.isArray(faultData) ? faultData.filter((x) => x.id) : []);
    for (const c of concepts) {
      items.push({
        id: `cgi-fault:${c.id}`,
        type: "fault_type",
        title: c.label_pt || c.label_en || c.id,
        title_en: c.label_en,
        text: [c.label_pt, c.label_en, c.definition].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([c.label_pt, c.label_en, c.id, c.definition].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  // CGI Deformation Style
  const cgiDeformPath = path.join(ROOT, "data", "cgi-deformation-style.json");
  if (fs.existsSync(cgiDeformPath)) {
    const deformData = JSON.parse(fs.readFileSync(cgiDeformPath, "utf8"));
    const concepts =
      deformData.concepts || (Array.isArray(deformData) ? deformData.filter((x) => x.id) : []);
    for (const c of concepts) {
      items.push({
        id: `cgi-deform:${c.id}`,
        type: "deformation_style",
        title: c.label_pt || c.label_en || c.id,
        title_en: c.label_en,
        text: [c.label_pt, c.label_en, c.definition].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([c.label_pt, c.label_en, c.id, c.definition].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  // CGI Contact Type
  const cgiContactPath = path.join(ROOT, "data", "cgi-contact-type.json");
  if (fs.existsSync(cgiContactPath)) {
    const contactData = JSON.parse(fs.readFileSync(cgiContactPath, "utf8"));
    const concepts =
      contactData.concepts || (Array.isArray(contactData) ? contactData.filter((x) => x.id) : []);
    for (const c of concepts) {
      items.push({
        id: `cgi-contact:${c.id}`,
        type: "contact_type",
        title: c.label_pt || c.label_en || c.id,
        title_en: c.label_en,
        text: [c.label_pt, c.label_en, c.definition].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([c.label_pt, c.label_en, c.id, c.definition].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  // CGI Stratigraphic Rank
  const cgiStratPath = path.join(ROOT, "data", "cgi-stratigraphic-rank.json");
  if (fs.existsSync(cgiStratPath)) {
    const stratData = JSON.parse(fs.readFileSync(cgiStratPath, "utf8"));
    const concepts =
      stratData.concepts || (Array.isArray(stratData) ? stratData.filter((x) => x.id) : []);
    for (const c of concepts) {
      items.push({
        id: `cgi-strat:${c.id}`,
        type: "stratigraphic_rank",
        title: c.label_pt || c.label_en || c.id,
        title_en: c.label_en,
        text: [c.label_pt, c.label_en, c.definition].filter(Boolean).join(". "),
        tokens: Array.from(
          new Set(tokenize([c.label_pt, c.label_en, c.id, c.definition].join(" ")))
        ),
        layer: "layer1b",
      });
    }
  }

  return { meta: { version: VERSION, generated: NOW, count: items.length }, items };
}

/* ─────────────────────────────────────────────────────────────
 * RAG CORPUS — JSONL
 * ───────────────────────────────────────────────────────────── */

function datasetTitle(id) {
  const c = CONJUNTOS.find((x) => x.id === id);
  return c ? c.titulo : id;
}

function loadAcronyms() {
  const p = path.join(ROOT, "data/acronyms.json");
  if (!fs.existsSync(p)) return null;
  const data = JSON.parse(fs.readFileSync(p, "utf8"));
  /* Apply 3W acronym enrichment patches (adds linked_entity_id, threew_role) */
  if (Array.isArray(data.acronyms)) {
    for (const patch of THREEW_ACRONYM_LINKS) {
      const item = data.acronyms.find((a) => a.id === patch.id);
      if (item) Object.assign(item, patch);
    }
  }
  return data;
}

/**
 * Builds the full RAG (Retrieval-Augmented Generation) corpus as an array of
 * JSONL-serialisable chunk objects. Combines chunks of types: term (ANP
 * glossary + extended terms), ontology_layer, column (dataset schema), entity,
 * domain, typology, processing level, OntoPetro classes/properties/relations/
 * instances, taxonomies, systems, module M7-M10 summaries and per-class chunks,
 * ambiguity alerts, PVT fields, NER mappings, GSO classes, seismic chunks,
 * geomechanics chunks, and OSDU tripartition RAG chunks. Written to
 * `ai/rag-corpus.jsonl`.
 *
 * @returns {Array<{id: string, type: string, text: string, metadata: Object}>}
 */
function buildRagCorpus() {
  const lines = [];

  /* type=term — glossário ANP enriquecido com sinônimos/exemplos + alinhamento */
  for (const t of GLOSSARIO) {
    const enrich = enrichmentFor(t.id);
    const align = alignmentFor(TERM_ALIGNMENT, t.id);
    const datasetTitles = (t.apareceEm || []).map(datasetTitle).join(", ");
    const synLine = enrich.synonyms_pt.length
      ? ` Sinônimos: ${[...enrich.synonyms_pt, ...enrich.synonyms_en].join(", ")}.`
      : "";
    const exLine = enrich.examples.length ? ` Exemplos: ${enrich.examples.join("; ")}.` : "";
    const enLine = enrich.termo_en ? ` (${enrich.termo_en})` : "";
    const text = `${t.termo}${enLine}: ${t.definicao}${synLine}${exLine}${datasetTitles ? ` Aparece nos datasets: ${datasetTitles}.` : ""} Fonte: ${t.fonte}.`;
    lines.push({
      id: `term_${t.id}`,
      type: "term",
      text,
      metadata: {
        id: t.id,
        category: t.categoria,
        legal_source: t.fonte,
        petrokgraph_uri: align.petrokgraph_uri,
        osdu_kind: align.osdu_kind,
        geocoverage: align.geocoverage,
        datasets: t.apareceEm || [],
      },
    });
  }

  /* type=term — extended-terms (geologia formal) */
  for (const t of EXTENDED_TERMS) {
    const synLine = t.synonyms_pt.length
      ? ` Sinônimos: ${[...t.synonyms_pt, ...t.synonyms_en].join(", ")}.`
      : "";
    const exLine = t.examples.length ? ` Exemplos: ${t.examples.join("; ")}.` : "";
    const text = `${t.termo} (${t.termo_en}): ${t.definicao}${synLine}${exLine} Fonte: ${t.legal_source}.`;
    lines.push({
      id: `term_${t.id}`,
      type: "term",
      text,
      metadata: {
        id: t.id,
        category: t.categoria,
        legal_source: t.legal_source,
        petrokgraph_uri: t.petrokgraph_uri,
        osdu_kind: t.osdu_kind,
        geocoverage: t.geocoverage,
        extended: true,
      },
    });
  }

  /* type=ontology_layer — descreve cada uma das 5 camadas semânticas */
  for (const layer of LAYER_DEFINITIONS) {
    const coverageList = Array.isArray(layer.geolytics_coverage)
      ? layer.geolytics_coverage.join(", ")
      : layer.geolytics_coverage;
    const text = `${layer.name} (${layer.id}, mantida por ${layer.maintainer}): ${layer.description}${layer.relationship_to_geocore ? ` Relação com GeoCore: ${layer.relationship_to_geocore}.` : ""} Cobertura no GeoBrain: ${coverageList}.`;
    lines.push({
      id: `ontology_layer_${layer.id}`,
      type: "ontology_layer",
      text,
      metadata: {
        layer: layer.id,
        name: layer.name,
        type: layer.type,
        maintainer: layer.maintainer,
      },
    });
  }

  /* type=column */
  for (const c of CONJUNTOS) {
    for (const col of c.colunas) {
      const text = `Coluna "${col.nome}" do dataset "${c.titulo}" (${c.id}): ${col.descricao}. Tipo: ${col.tipo}. Fonte do dataset: ${c.fonte}. Frequência: ${c.frequencia}.`;
      lines.push({
        id: `column_${c.id}_${col.nome
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, "_")
          .replace(/^_|_$/g, "")}`,
        type: "column",
        text,
        metadata: {
          dataset_id: c.id,
          dataset_title: c.titulo,
          column_name: col.nome,
          column_type: col.tipo,
          source: c.fonte,
        },
      });
    }
  }

  /* type=entity */
  for (const n of buildEntityGraph().nodes) {
    const outRels = EDGES.filter((e) => e.source === n.id).map(
      (e) => `${e.relation_label} ${ENTITY_NODES.find((x) => x.id === e.target)?.label || e.target}`
    );
    const text = `Entidade "${n.label}" (${n.label_en}), tipo ${n.type}. ${n.definition}${outRels.length ? ` Relações: ${outRels.join("; ")}.` : ""}${n.legal_source ? ` Fonte: ${n.legal_source}.` : ""}`;
    lines.push({
      id: `entity_${n.id}`,
      type: "entity",
      text,
      metadata: {
        id: n.id,
        entity_type: n.type,
        label_en: n.label_en,
        legal_source: n.legal_source,
        datasets: n.datasets,
      },
    });
  }

  /* type=domain */
  for (const d of DOMAINS) {
    lines.push({
      id: `domain_${d.id}`,
      type: "domain",
      text: `Domínio Geolytics "${d.label}": ${d.desc}. Os domínios organizam os termos do dicionário ANP em quatro grupos primários: Ativos (ciclo contratual e regulatório), Fluidos (produção e injeção), Rocha (geologia sedimentar) e Geomecânica (estrutura física dos poços).`,
      metadata: { id: d.id, label: d.label },
    });
  }

  /* type=type — tipologia geoquímica */
  for (const item of ONTOLOGY_TYPES.tipologia.items) {
    lines.push({
      id: `type_typology_${item.id}`,
      type: "type",
      text: `Tipologia geoquímica "${item.label}": ${item.desc}. Categoria que classifica o que o dado representa quimicamente ou operacionalmente, dentro da ontologia de dados geoquímicos do Geolytics.`,
      metadata: { id: item.id, group: "typology", label: item.label },
    });
  }
  /* type=type — níveis de processamento */
  for (const item of ONTOLOGY_TYPES.nivel.items) {
    lines.push({
      id: `type_processing_${item.id}`,
      type: "type",
      text: `Nível de processamento "${item.label}": ${item.desc}. Indica o grau de transformação do dado bruto até o produto analítico final.`,
      metadata: { id: item.id, group: "processing_level", label: item.label },
    });
  }

  /* type=ontopetro_class — 20 classes do Módulo 1 */
  for (const c of ONTOPETRO_CLASSES) {
    const text = `Classe ontopetro "${c.name}" (${c.name_en}, superclasse ${c.superclass}): ${c.description}. Domínio: ${c.domain}. Fontes: ${c.sources.join(", ")}.${c.entity_graph_id ? ` Mapeada ao nó do grafo: ${c.entity_graph_id}.` : ""}`;
    lines.push({
      id: `ontopetro_class_${c.id}`,
      type: "ontopetro_class",
      text,
      metadata: {
        id: c.id,
        name: c.name,
        superclass: c.superclass,
        sources: c.sources,
        entity_graph_id: c.entity_graph_id,
      },
    });
  }
  /* type=ontopetro_property — propriedades com unidade (alta prioridade RAG) */
  for (const p of ONTOPETRO_PROPERTIES.filter((x) => x.rag_priority === "high")) {
    const text = `Propriedade ontopetro "${p.name}" (${p.name_en || p.name}): ${p.description}. Domínio: ${p.domain_class}. Range: ${p.range}.${p.unit ? ` Unidade: ${p.unit}.` : ""}`;
    lines.push({
      id: `ontopetro_property_${p.id}`,
      type: "ontopetro_property",
      text,
      metadata: { id: p.id, name: p.name, unit: p.unit, domain_class: p.domain_class },
    });
  }
  /* type=ontopetro_relation */
  for (const r of ONTOPETRO_RELATIONS) {
    const text = `Relação ontopetro "${r.name}" (${r.name_en}): ${r.description}. ${r.domain} → ${r.range} (cardinalidade ${r.cardinality}). Inversa: ${r.inverse || "sem"}.`;
    lines.push({
      id: `ontopetro_relation_${r.id}`,
      type: "ontopetro_relation",
      text,
      metadata: {
        id: r.id,
        name: r.name,
        domain: r.domain,
        range: r.range,
        cardinality: r.cardinality,
      },
    });
  }
  /* type=instance_ref — instâncias I001-I010 */
  for (const i of ONTOPETRO_INSTANCES) {
    const attrs = Object.entries(i.attributes || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join("; ");
    const text = `Instância de referência (${i.id}) "${i.name}" — classe ${i.class}.${attrs ? ` Atributos: ${attrs}.` : ""} Fonte: ${i.source}.`;
    lines.push({
      id: `instance_${i.id}`,
      type: "instance_ref",
      text,
      metadata: { id: i.id, class: i.class, name: i.name, source: i.source },
    });
  }

  /* type=taxonomy — 9 enumerações do ontopetro M5 */
  for (const [key, t] of Object.entries(TAXONOMIES)) {
    const valuesDesc = Array.isArray(t.values)
      ? t.values.join(", ")
      : Object.keys(t.values).join(", ");
    const alert = t.rag_alert ? ` ALERTA: ${t.rag_alert}` : "";
    const text = `Taxonomia "${t.label}" (${t.label_en || t.label}): ${t.description || `Enumeração canônica de ${t.label}`}. Valores: ${valuesDesc}.${alert}`;
    lines.push({
      id: `taxonomy_${key}`,
      type: "taxonomy",
      text,
      metadata: { key, label: t.label, has_alert: !!t.rag_alert },
    });
  }

  /* type=system_ref — 8 sistemas corporativos Petrobras */
  for (const s of SYSTEMS) {
    const text = `Sistema corporativo Petrobras "${s.name}" (${s.id}, tipo ${s.type}, domínio ${s.domain}): ${s.description} Objetos de dados: ${s.data_objects.join(", ")}. NOTA: este é metadado de proveniência, não de acesso — agentes não devem tentar conectar.`;
    lines.push({
      id: `system_${s.id}`,
      type: "system_ref",
      text,
      metadata: { id: s.id, type: s.type, domain: s.domain },
    });
  }

  /* type=module_extended — M7/M8/M9/M10 visão geral + classes-chave */
  for (const [key, m] of Object.entries(MODULES_EXTENDED)) {
    const classList = m.classes
      .slice(0, 8)
      .map((c) => `${c.id}=${c.name}`)
      .join("; ");
    const propList = (m.key_properties || [])
      .slice(0, 6)
      .map((p) => `${p.name}${p.unit ? ` [${p.unit}]` : ""}`)
      .join("; ");
    const cross = m.cross_module_connections
      ? ` Conexões cross-módulo: ${m.cross_module_connections.map((c) => `${c.from}→${c.to}: ${c.connection}`).join(". ")}.`
      : "";
    const text = `Módulo ${key} — ${m.label} (${m.label_en}). Sistemas-fonte: ${m.system_origin}. Classes principais: ${classList}. Propriedades-chave: ${propList}.${cross}`;
    lines.push({
      id: `module_${key}`,
      type: "module_extended",
      text,
      metadata: { module: key, label: m.label, system_origin: m.system_origin },
    });
    /* Chunks individuais por classe — granularidade RAG por C-ID */
    for (const c of m.classes) {
      lines.push({
        id: `class_${key}_${c.id}`,
        type: `module_class_${key.split("_")[0]}` /* module_class_M7, module_class_M8, etc. */,
        text: `Classe ${c.id} "${c.name}" do módulo ${m.label} (${m.label_en}, sistema-fonte ${m.system_origin}). Superclasse: ${c.superclass}. ${c.description}`,
        metadata: {
          id: c.id,
          name: c.name,
          module: key,
          superclass: c.superclass,
          system_origin: m.system_origin,
        },
      });
    }
    /* Chunks por propriedade-chave — recall por unidade/sigla técnica */
    for (const p of m.key_properties || []) {
      lines.push({
        id: `prop_${key}_${p.id}`,
        type: `module_property_${key.split("_")[0]}`,
        text: `Propriedade ${p.id} "${p.name}"${p.name_en ? ` (${p.name_en})` : ""} do módulo ${m.label}. ${p.description}${p.unit ? ` Unidade: ${p.unit}.` : ""} Sistema-fonte: ${m.system_origin}.`,
        metadata: { id: p.id, name: p.name, unit: p.unit, module: key },
      });
    }
  }

  /* type=pvt_property — campos PVT com completude real (top 10 por relevância) */
  const pvtImportant = PVT_FIELDS.filter((f) =>
    /API|RGO|Psat|Press|Bacia|Poço|Campo|Temperatura|Fluido/i.test(f.name)
  ).slice(0, 12);
  for (const f of pvtImportant) {
    const text = `Campo PVT do sistema SIRR "${f.name}" (tipo ${f.type}): ${f.description}.${f.unit ? ` Unidade: ${f.unit}.` : ""} Completude na base corporativa: ${f.completeness_pct.toFixed(1)}%.`;
    lines.push({
      id: `pvt_${f.name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_|_$/g, "")}`,
      type: "pvt_property",
      text,
      metadata: { name: f.name, completeness_pct: f.completeness_pct, source: "SIRR" },
    });
  }

  /* type=ambiguity_alert — 13 chunks críticos para LLMs em O&G PT-BR */
  for (const a of AMBIGUITY_ALERTS) {
    lines.push({
      id: a.id,
      type: "ambiguity_alert",
      text: a.text,
      metadata: { terms: a.terms, priority: "high" },
    });
  }

  /* type=ner_mapping — schema PetroGold */
  for (const m of REGIS_NER_MAPPINGS) {
    const text = `Mapeamento NER PetroGold tipo "${m.petrogold_type}" (${m.petrogold_label}) → nós do Geolytics: ${m.geolytics_nodes.join(", ")}. ${m.disambiguation_note} Exemplos: ${m.example_entities.join("; ")}.`;
    lines.push({
      id: `ner_mapping_${m.petrogold_type.toLowerCase()}`,
      type: "ner_mapping",
      text,
      metadata: { petrogold_type: m.petrogold_type, geolytics_nodes: m.geolytics_nodes },
    });
  }

  /* type=osdu_tripartition + osdu_kind_mapping — increment v2 */
  for (const c of OSDU_RAG_CHUNKS) {
    lines.push({ id: c.id, type: c.type, text: c.text, metadata: c.metadata });
  }

  /* type=acronym — siglas O&G (filtra it_generic) */
  const ac = loadAcronyms();
  if (ac && Array.isArray(ac.acronyms)) {
    for (const a of ac.acronyms) {
      if (a.it_generic) continue;
      const parts = [
        `${a.sigla}`,
        a.expansion_pt ? `(${a.expansion_pt})` : null,
        a.expansion_en ? `— ${a.expansion_en}` : null,
      ]
        .filter(Boolean)
        .join(" ");
      const text = `Sigla "${a.sigla}" do domínio O&G, categoria ${a.category}. ${parts}.`;
      lines.push({
        id: `acronym_${a.id}`,
        type: "acronym",
        text,
        metadata: {
          sigla: a.sigla,
          category: a.category,
          expansion_pt: a.expansion_pt,
          expansion_en: a.expansion_en,
        },
      });
    }
  }

  /* type=ontology_class — GSO (Layer 7, Loop3D Geoscience Ontology) */
  for (const mod of loadGsoModules()) {
    for (const [key, c] of Object.entries(mod.classes)) {
      const labels = [c.pref_label_en, c.pref_label_fr].filter(Boolean).join(" / ");
      const parents = (c.parents || []).join(", ");
      const sources = (c.sources || []).join("; ");
      const text = `${labels || c.gso_class} (GSO ${c.gso_class}): ${c.definition_en_canonical || "(no definition)"}${parents ? ` Subclasse de: ${parents}.` : ""}${sources ? ` Fonte: ${sources}.` : ""} Camada 7 (GSO/Loop3D, CC BY 4.0).`;
      lines.push({
        id: `gso_${mod.meta.module.replace(/^GSO-/, "").toLowerCase()}_${c.gso_class}`,
        type: "ontology_class",
        text,
        metadata: {
          gso_class: c.gso_class,
          owl_uri: c.owl_uri,
          parents: c.parents,
          sources: c.sources,
          layer: "layer7",
          module: mod.meta.module,
          license: "CC BY 4.0",
          attribution: mod.meta.attribution,
        },
      });
    }
  }

  /* type=seismic_class / seismic_attribute — P2.8 Seismic module */
  for (const chunk of buildSeismicRagChunks()) {
    lines.push(chunk);
  }

  /* type=geomec_class / geomec_property / geomec_instance — P2.7 MEM module */
  const gm = loadGeomechanics();
  if (gm) {
    for (const c of gm.classes || []) {
      const alert = c.rag_alert ? ` ALERTA RAG: ${c.rag_alert}` : "";
      const sweet = c.sweet_alignment ? ` SWEET: ${c.sweet_alignment}.` : "";
      const sources = Array.isArray(c.sources) ? ` Fontes: ${c.sources.join("; ")}.` : "";
      const geo = c.geocoverage ? ` Cobertura geográfica: ${c.geocoverage}.` : "";
      const text = `Classe geomecânica ${c.id} "${c.name}" (${c.name_en || c.name}): ${c.definition}${sweet}${sources}${geo}${alert}`;
      lines.push({
        id: `geomec_class_${c.id}`,
        type: "geomec_class",
        text,
        metadata: {
          id: c.id,
          name: c.name,
          sweet_alignment: c.sweet_alignment,
          geocoverage: c.geocoverage,
          has_alert: !!c.rag_alert,
        },
      });
    }
    for (const p of gm.properties || []) {
      const unitStr = p.unit ? ` Unidade: ${p.unit}.` : "";
      const rangeStr =
        p.min_value !== undefined && p.max_value !== undefined
          ? ` Faixa válida: ${p.min_value}–${p.max_value}.`
          : "";
      const alert = p.rag_alert ? ` ALERTA RAG: ${p.rag_alert}` : "";
      const text = `Propriedade geomecânica ${p.id} "${p.name}" (${p.name_en || p.name}): ${p.description}${unitStr}${rangeStr}${alert}`;
      lines.push({
        id: `geomec_property_${p.id}`,
        type: "geomec_property",
        text,
        metadata: { id: p.id, name: p.name, unit: p.unit || null, has_alert: !!p.rag_alert },
      });
    }
    for (const inst of gm.instances || []) {
      const attrs = Object.entries(inst.attributes || {})
        .map(([k, v]) => `${k}: ${v}`)
        .join("; ");
      const text = `Instância geomecânica "${inst.id}" — classe ${inst.class} (${inst.name}).${attrs ? ` Atributos: ${attrs}.` : ""} Fonte: ${inst.source}.`;
      lines.push({
        id: `geomec_instance_${inst.id}`,
        type: "geomec_instance",
        text,
        metadata: { id: inst.id, class: inst.class, name: inst.name, source: inst.source },
      });
    }
  }

  /* type=geomec_corporate_entity — L6 corporate module (P2.10) */
  const gmCorpPath = path.resolve(__dirname, "..", "data", "geomechanics-corporate.json");
  if (fs.existsSync(gmCorpPath)) {
    const gmCorp = JSON.parse(fs.readFileSync(gmCorpPath, "utf8"));
    for (const e of gmCorp.entities || []) {
      if (e.deprecated) continue;
      const conf = e.confidence ? ` [confiança: ${e.confidence}]` : "";
      const def = e.definition_pt || e.definition || "";
      const formulaStr = e.formula ? ` Fórmula: ${e.formula}.` : "";
      const gapStr =
        e.evidence_gaps && e.evidence_gaps.length
          ? ` Lacunas de evidência: ${e.evidence_gaps.join("; ")}.`
          : "";
      const oosStr = e.out_of_scope_flag ? " [OUT_OF_SCOPE]" : "";
      const provStr = (e.obtained_from_lab_tests || [])
        .map((p) => `${p.test_label}${p.primary ? " (primário)" : ""}: ${p.method_note}`)
        .join(" | ");
      const provBlock = provStr ? ` Métodos de obtenção: ${provStr}.` : "";
      const text = `Entidade corporativa ${e.id} "${e.label_pt || e.label}"${conf}: ${def}${formulaStr}${gapStr}${provBlock}${oosStr}`;
      lines.push({
        id: `geomec_corporate_entity_${e.id}`,
        type: "geomec_corporate_entity",
        text,
        metadata: {
          id: e.id,
          category: e.category,
          confidence: e.confidence || null,
          layer: "L6",
          out_of_scope: !!e.out_of_scope_flag,
          lab_test_method_count: (e.obtained_from_lab_tests || []).length,
          primary_lab_test:
            ((e.obtained_from_lab_tests || []).find((p) => p.primary) || {}).test_id || null,
        },
      });
    }
  }

  /* type=lithology — CGI Simple Lithology 2021 (layer1b) */
  for (const chunk of buildLithologyRagChunks()) {
    lines.push(chunk);
  }

  /* type=geologic_time — ICS/CGI Geologic Time 2023 (layer3) */
  for (const chunk of buildGeologicTimeRagChunks()) {
    lines.push(chunk);
  }

  /* type=fault_type / deformation_style / contact_type / stratigraphic_rank — T6 structural vocabs */
  for (const chunk of buildCgiVocabChunks("cgi-fault-type.json", "fault_type")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("cgi-deformation-style.json", "deformation_style")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("cgi-contact-type.json", "contact_type")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("cgi-stratigraphic-rank.json", "stratigraphic_rank")) {
    lines.push(chunk);
  }

  /* type=anp_* — ANP-699/2017 controlled vocabularies (layer4 regulatory) */
  for (const chunk of buildCgiVocabChunks("anp-poco-categoria.json", "anp_poco_categoria")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("anp-poco-tipo.json", "anp_poco_tipo")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("anp-poco-resultado.json", "anp_poco_resultado")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("anp-uf.json", "anp_uf")) {
    lines.push(chunk);
  }
  for (const chunk of buildCgiVocabChunks("anp-bacia-sedimentar.json", "anp_bacia_sedimentar")) {
    lines.push(chunk);
  }

  /* type=anp699_doc — 18 ANP-699 regulatory document classes + Poco entity */
  for (const chunk of buildAnp699RagChunks()) {
    lines.push(chunk);
  }
  /* type=gpp_class — 28 governance/lifecycle/portfolio classes from GPP module */
  for (const chunk of buildGppRagChunks()) {
    lines.push(chunk);
  }

  /* type=threew_event — 3W Petrobras operational event classes */
  for (const chunk of THREEW_RAG_CHUNKS) {
    lines.push(chunk);
  }

  return lines.map((l) => JSON.stringify(l)).join("\n") + "\n";
}

/* ─────────────────────────────────────────────────────────────
 * CGI SIMPLE LITHOLOGY — RAG chunks (layer1b)
 * Source: data/cgi-lithology.json + data/cgi-osdu-lithology-map.json
 * ───────────────────────────────────────────────────────────── */

/**
 * Builds RAG corpus chunks for the CGI Simple Lithology vocabulary by loading
 * `data/cgi-lithology.json` and `data/cgi-osdu-lithology-map.json`. Each
 * of the ~437 CGI lithology concepts becomes a chunk with its OSDU
 * LithologyType mapping, preferred labels, and SKOS hierarchy. Returns an
 * empty array and emits a warning when the source files are absent.
 *
 * @returns {Array<{id: string, type: string, text: string, metadata: Object}>}
 */
function buildLithologyRagChunks() {
  const lithPath = path.join(ROOT, "data", "cgi-lithology.json");
  const mapPath = path.join(ROOT, "data", "cgi-osdu-lithology-map.json");
  if (!fs.existsSync(lithPath) || !fs.existsSync(mapPath)) {
    console.warn("  [warn] CGI lithology data files not found, skipping lithology chunks");
    return [];
  }

  const lithData = JSON.parse(fs.readFileSync(lithPath, "utf8"));
  const mapData = JSON.parse(fs.readFileSync(mapPath, "utf8"));

  /* Build lookup: cgi_id -> { value, match_kind } */
  const osduLookup = new Map();
  for (const m of mapData.mappings || []) {
    if (m.cgi_id && !osduLookup.has(m.cgi_id)) {
      osduLookup.set(m.cgi_id, { value: m.osdu_value, match_kind: m.match_kind });
    }
  }

  const chunks = [];
  for (const concept of lithData.concepts || []) {
    const rawDef = concept.definition_en
      ? concept.definition_en.length > 500
        ? concept.definition_en.slice(0, 497) + "..."
        : concept.definition_en
      : null;
    /* Fall back to label when no formal definition is available (412/437 QAPF concepts) */
    const defText = rawDef || `Conceito litológico CGI: ${concept.label_pt || concept.label_en}.`;
    const osduMapping = osduLookup.get(concept.id) || null;
    const parents = concept.parents || [];
    const parentStr = parents.length ? ` Hierarquia: ${parents.join(" > ")}.` : "";
    const osduStr = osduMapping
      ? ` OSDU LithologyType: ${osduMapping.value} (${osduMapping.match_kind || "match"}).`
      : "";
    const text =
      `${concept.label_en} (${concept.label_pt || concept.label_en}): ${defText}${parentStr}${osduStr} URI: ${concept.uri || ""}.`.trim();
    chunks.push({
      id: `cgi-lith-${concept.id}`,
      type: "lithology",
      text,
      metadata: {
        id: concept.id,
        label_pt: concept.label_pt || null,
        label_en: concept.label_en || null,
        definition: rawDef,
        parents,
        osdu_mapping: osduMapping,
        uri: concept.uri || null,
        layer: "layer1b",
        source: "CGI_SimpleLithology_2021",
      },
    });
  }
  console.log(`  ✓ CGI lithology chunks: ${chunks.length}`);
  return chunks;
}

/* ─────────────────────────────────────────────────────────────
 * CGI GEOLOGIC TIME — RAG chunks (layer3)
 * Source: data/cgi-geologic-time.json
 * ───────────────────────────────────────────────────────────── */

/**
 * Builds RAG chunks for the ICS 2023 Geologic Time Scale.
 * Emits one chunk per unit (eon/era/period/epoch/age) with PT-BR labels,
 * time bounds (Ma), parent, and Brazil-specific stratigraphic notes.
 *
 * @returns {Array<Object>} RAG chunks with type='geologic_time', layer='layer3'
 */
function buildGeologicTimeRagChunks() {
  const filePath = path.join(ROOT, "data", "cgi-geologic-time.json");
  if (!fs.existsSync(filePath)) {
    console.warn("  [warn] cgi-geologic-time.json not found, skipping geologic time chunks");
    return [];
  }
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return (data.units || []).map((unit) => {
    const maStr =
      unit.start_ma != null && unit.end_ma != null ? ` ${unit.start_ma}–${unit.end_ma} Ma.` : "";
    const brazilStr = unit.brazil_notes ? ` Brasil: ${unit.brazil_notes}.` : "";
    const parentStr = unit.parent ? ` Pertence a: ${unit.parent}.` : "";
    const text =
      `${unit.label_en} (${unit.label_pt || unit.label_en}): Unidade cronoestratigráfica ${unit.rank || "geológica"}.${maStr}${brazilStr}${parentStr} URI: ${unit.uri || ""}.`.trim();
    return {
      id: `cgi-time-${unit.id}`,
      type: "geologic_time",
      text,
      metadata: {
        id: unit.id,
        label_pt: unit.label_pt || null,
        label_en: unit.label_en || null,
        rank: unit.rank || null,
        start_ma: unit.start_ma ?? null,
        end_ma: unit.end_ma ?? null,
        parent: unit.parent || null,
        brazil_notes: unit.brazil_notes || null,
        uri: unit.uri || null,
        layer: "layer3",
        source: "ICS_2023",
      },
    };
  });
}

/**
 * Generic builder for CGI vocabulary RAG chunks.
 * Reads a CGI vocab JSON file (with `concepts` or `units` array) and
 * emits one chunk per concept with labels, definition, hierarchy, and entity link.
 *
 * @param {string} filename - Basename of the JSON file in data/ (e.g. 'cgi-fault-type.json')
 * @param {string} chunkType - Value for the chunk's `type` field (e.g. 'fault_type')
 * @returns {Array<Object>} RAG chunks for the vocabulary
 */
function buildCgiVocabChunks(filename, chunkType) {
  const filePath = path.join(ROOT, "data", filename);
  if (!fs.existsSync(filePath)) {
    console.warn(`  [warn] ${filename} not found, skipping ${chunkType} chunks`);
    return [];
  }
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const items = data.concepts || data.units || [];
  const source = (data.meta && data.meta.source) || "CGI";
  /* Layer: read from meta if present (e.g. ANP codelists declare "layer4"),
     fallback to "layer1b" for legacy CGI vocabularies that omit the field. */
  const layer = (data.meta && data.meta.layer) || "layer1b";
  return items.map((item) => {
    const rawDef = item.definition ? item.definition.slice(0, 500) : null;
    /* Fallback: synthesise a minimal description when no definition is present */
    const defText =
      rawDef || `Conceito ${chunkType.replace(/_/g, " ")}: ${item.label_pt || item.label_en}.`;
    const broaderStr = item.broader ? ` Broader: ${item.broader}.` : "";
    const relStr = item.related_entity ? ` Entidade relacionada: ${item.related_entity}.` : "";
    const parentsStr = (item.parents || []).length
      ? ` Hierarquia: ${item.parents.join(" > ")}.`
      : "";
    const anpStr = item.anp_code ? ` Código ANP: ${item.anp_code}.` : "";
    const ambienteStr = item.ambiente ? ` Ambiente: ${item.ambiente}.` : "";
    const text =
      `${item.label_en || item.label_pt} (${item.label_pt || item.label_en}): ${defText}${anpStr}${ambienteStr}${broaderStr}${parentsStr}${relStr} URI: ${item.uri || ""}.`.trim();
    return {
      id: `${chunkType}-${item.id}`,
      type: chunkType,
      text,
      metadata: {
        id: item.id,
        label_pt: item.label_pt || null,
        label_en: item.label_en || null,
        anp_code: item.anp_code || null,
        ambiente: item.ambiente || null,
        definition: rawDef,
        broader: item.broader || null,
        parents: item.parents || [],
        related_entity: item.related_entity || null,
        uri: item.uri || null,
        layer,
        source,
      },
    };
  });
}

/* ─────────────────────────────────────────────────────────────
 * ANP-699 DOC CLASSES — auto-emit RAG chunks from operacoes-geologicas.json
 * ─────────────────────────────────────────────────────────────
 * Source-of-truth is data/operacoes-geologicas.json. Avoids duplicating
 * fully-baked nodes for the 18 ANP-699 doc classes + Poco class added in
 * Phase 4. Filters by `evidence_refs` containing "ANP-699/2017".
 */
function buildAnp699RagChunks() {
  const ogPath = path.join(ROOT, "data", "operacoes-geologicas.json");
  if (!fs.existsSync(ogPath)) return [];
  const og = JSON.parse(fs.readFileSync(ogPath, "utf8"));
  const chunks = [];
  for (const [name, cls] of Object.entries(og.classes || {})) {
    const refs = cls.evidence_refs || [];
    const isAnp699 = refs.some((r) => typeof r === "string" && r.startsWith("ANP-699"));
    if (!isAnp699) continue;
    const sigla = (cls.label_pt || "").split(" — ")[0] || name;
    const def = (cls.description_pt || cls.description || "").slice(0, 800);
    const prazoStr = cls.prazo_envio ? ` Prazo de envio: ${cls.prazo_envio}.` : "";
    const gatStr = cls.gatilho ? ` Gatilho: ${cls.gatilho}.` : "";
    const formaStr = cls.forma_envio ? ` Forma: ${cls.forma_envio}.` : "";
    const synStr = (cls.synonyms || []).length ? ` Sinônimos: ${cls.synonyms.join("; ")}.` : "";
    const text =
      `${cls.label_pt || cls.label_en} (${cls.label_en || ""}): ${def}${prazoStr}${gatStr}${formaStr}${synStr} Fonte: ${refs.join("; ")}.`.trim();
    chunks.push({
      id: `anp699_doc_${cls.id || name}`,
      type: "anp699_doc",
      text,
      metadata: {
        id: cls.id || name,
        sigla,
        name,
        superclass: cls.superclass || null,
        prazo_envio: cls.prazo_envio || null,
        gatilho: cls.gatilho || null,
        forma_envio: cls.forma_envio || null,
        manager: cls.manager || null,
        stored_in: cls.stored_in || null,
        corporate_internal: !!cls.corporate_internal,
        evidence_refs: refs,
        layer: "layer4",
        source: "data/operacoes-geologicas.json",
      },
    });
  }
  return chunks;
}

/* GPP module — auto-emit RAG chunks for governance entities not already in
   GPP_NODES (e.g., new classes only present in data/gestao-projetos-parcerias.json).
   Avoids duplicating with existing entity-graph nodes. */
function buildGppRagChunks() {
  const gppPath = path.join(ROOT, "data", "gestao-projetos-parcerias.json");
  if (!fs.existsSync(gppPath)) return [];
  const gpp = JSON.parse(fs.readFileSync(gppPath, "utf8"));
  const chunks = [];
  for (const [name, cls] of Object.entries(gpp.classes || {})) {
    const def = (cls.description_pt || cls.description || "").slice(0, 800);
    const synStr = (cls.synonyms || []).length ? ` Sinônimos: ${cls.synonyms.join("; ")}.` : "";
    const exStr = (cls.examples_pt || []).length ? ` Exemplos: ${cls.examples_pt.join("; ")}.` : "";
    const corpFlag = cls.corporate_internal ? " [Petrobras-interno]" : "";
    const text =
      `${cls.label_pt || cls.label_en} (${cls.label_en || ""})${corpFlag}: ${def}${synStr}${exStr} Fonte: ${(cls.evidence_refs || []).join("; ")}.`.trim();
    chunks.push({
      id: `gpp_class_${cls.id || name}`,
      type: "gpp_class",
      text,
      metadata: {
        id: cls.id || name,
        name,
        superclass: cls.superclass || null,
        corporate_internal: !!cls.corporate_internal,
        governance_role: cls.governance_role || null,
        ontology_role: cls.ontology_role || null,
        lifecycle_state: !!cls.lifecycle_state,
        evidence_refs: cls.evidence_refs || [],
        layer: "layer4",
        source: "data/gestao-projetos-parcerias.json",
      },
    });
  }
  return chunks;
}

/* ─────────────────────────────────────────────────────────────
 * SYSTEM PROMPTS
 * ───────────────────────────────────────────────────────────── */

const SYSTEM_PROMPT_PT = `# Contexto de Domínio: Exploração e Produção de Petróleo no Brasil

## 1. Contexto regulatório

A Exploração e Produção (E&P) de petróleo e gás natural no Brasil é regulada pela **Agência Nacional do Petróleo, Gás Natural e Biocombustíveis (ANP)**, autarquia federal vinculada ao Ministério de Minas e Energia, criada pela **Lei nº 9.478/1997** (Lei do Petróleo). A ANP contrata, fiscaliza e regula todas as atividades exploratórias e produtivas do país. Os dados oficiais são publicados pela **Superintendência de Exploração (SEP)** através do **SIGEP — Sistema de Informações Gerenciais de Exploração e Produção**.

Este dicionário cobre 8 camadas semânticas: BFO+GeoCore (UFRGS), GeoSciML+CGI (OGC/IUGS — padrão internacional de boreholes e litologias), O3PO+GeoReservoir (UFRGS), Petro KGraph (PUC-Rio, 539 conceitos PT-BR), OSDU (industry standard), ANP/SIGEP (regulatório brasileiro), Geolytics/Petrobras Internal (módulos M7-M10) e GSO/Loop3D (geologia estrutural).

Existem dois regimes contratuais principais. Na **Concessão** (Lei 9.478/1997), o concessionário assume todos os riscos, detém o petróleo produzido e paga tributos (royalties, participação especial). Na **Partilha de Produção** (Lei 12.351/2010, aplicável ao polígono do pré-sal e áreas estratégicas), o petróleo é dividido entre contratado e União, e a **Petrobras é operadora obrigatória** nos blocos do pré-sal.

## 2. Entidades-chave

- **Poço (ANP)** — identificador padronizado de poço de óleo/gás (ex.: 1-RJS-702-RJ). No modelo GeoSciML (gsmlbh), o poço é representado pela classe **Borehole** com propriedades boreholeDiameter, dateOfDrilling e inclinationType; componentes de construção (revestimento, cimentação, tela, filtro) são modelados pelo módulo **GWML2 WellConstruction** (9 classes).
- **Bloco** — prisma vertical numa bacia sedimentar onde se realiza E&P; arrematado em rodada.
- **Bacia Sedimentar** — depressão crustal com rochas sedimentares (Campos, Santos, Recôncavo).
- **Campo / Área de Desenvolvimento** — área produtora resultante de Declaração de Comercialidade.
- **Contrato E&P** — instrumento jurídico entre concessionário e ANP; define regime contratual e período exploratório.
- **PAD — Plano de Avaliação de Descobertas** — avalia tecnicamente uma descoberta para viabilidade comercial; pode resultar em Declaração de Comercialidade.
- **Operador** — empresa designada para conduzir as operações; responde pela execução do contrato.
- **Rodada de Licitação** — leilão público de áreas de exploração.
- **Declaração de Comercialidade** — declaração formal de viabilidade econômica; encerra PAD com sucesso e origina um Campo.
- **Regime Contratual** — Concessão ou Partilha de Produção.
- **Pré-sal** — camada geológica abaixo de extensa camada de sal; reservatórios carbonáticos do pré-sal são o eixo da produção brasileira atual.
- **Reservatório** — corpo rochoso poroso e permeável que armazena hidrocarbonetos.

## 3. Termos que confundem LLMs — atenção especial

### 3.1 Regulatório / contratual
- **PAD ≠ "drilling pad"**: no contexto ANP, PAD = **Plano de Avaliação de Descobertas** (instrumento contratual), não base/locação física de perfuração.
- **UTS ≠ Unidade Territorial**: = **Unidades de Trabalho** — métrica do PEM (Programa Exploratório Mínimo).
- **Período Exploratório ≠ "período de exploração genérico"**: fase contratual específica (1º, 2º, 3º PE ou período único).
- **Concessão ≠ Partilha de Produção**: regimes contratuais distintos. Em Partilha, Petrobras é operadora obrigatória no pré-sal.

### 3.2 Geológico / produtivo
- **Pré-sal**: estritamente geológica (camada abaixo do sal). Atingir o pré-sal tem consequências contratuais.
- **Campo ≠ Bloco ≠ Bacia**: três entidades distintas — Campo (produção), Bloco (contrato), Bacia (geologia).
- **Reservatório ≠ Campo**: reservatório é corpo rochoso; campo é delimitação econômico-administrativa.
- **Reserva ≠ Reservatório ≠ Reserva Ambiental**: tripla polissemia. Reserva (SPE-PRMS) é volume econômico (1P/2P/3P); reservatório é geológico; reserva ambiental é REBIO/RPPN.
- **Formação ≠ litologia**: erro NER mais comum em PT-BR. *Formação Barra Velha* (FOR) é nome próprio de unidade litoestratigráfica; *calcário microbialítico* (ROC) é o tipo petrográfico que a compõe. O vocabulário canônico de litologias é o **CGI Simple Lithology** (437 conceitos, disponível em PT e EN, adotado pelo OSDU como referência para LithologyType). Exemplos: limestone, dolostone, arenite, rock_salt, anhydrite — sempre verificar o termo CGI antes de mapear litologia OSDU.
- **CGI vocabulários estruturais**: além de litologias, CGI/GeoSciML define vocabulários para tipos de falha, estilos de deformação, tipos de contato e ranques estratigráficos — use ao descrever geologia estrutural no contexto GeoSciML (gsmlb).
- **Campo (polissemia)**: pode ser Campo (ANP — Búzios), campo (atributo de dado), campo (geográfico), Campo Tensional (M9). Sempre desambiguar.
- **Intervalo ≠ Idade**: NER PetroGold INT (intervalo 2100-2450m) ≠ IDA (Aptiano). Um intervalo *tem* uma idade, mas não é a idade.

### 3.3 Geoquímica (M7) e PVT (M10)
- **RGO ≡ GOR**: Razão Gás-Óleo (PT) e Gas-Oil Ratio (EN) são SINÔNIMOS. Unidades scf/stb (EN) ou m³/m³ (SI). Base SIRR campo "RGO Tanque".
- **COT ≡ TOC**: Carbono Orgânico Total (PT) ≡ Total Organic Carbon (EN). COT > 1% = potencial gerador; > 2% = excelente. Rock-Eval.
- **Janela de Lama ≠ Janela de Geração**: a primeira é intervalo seguro de peso de lama (M9 Geomecânica, limites colapso/fratura); a segunda é faixa de Ro% para geração de HC (M7 Geoquímica, 0.5–2.0%).
- **API Tanque ≠ API Reservatório**: medido em superfície (após gás sair) vs in situ. SIRR usa "Grau API Tanque".

### 3.4 Geomecânica (M9) e Petrofísica (M8)
- **UCS estático ≠ UCS dinâmico**: estático = lab (verdadeiro); dinâmico = derivado de DTC/DTS via correlação GDA/Petrobras. Diferença típica 20–40%. Não usar dinâmico para projeto sem calibração.
- **Sv / Shmin / SHmax**: três tensores distintos do CampoTensionalInSitu. Em regime extensional Sv > SHmax > Shmin (regime normal); compressional inverte a ordem.
- **Porosidade NMR / Den / Neu / Son**: não é única. NMR é mais precisa em carbonatos pré-sal; Den assume densidade da matriz; Neu é sensível ao hidrogênio total; Son subestima em carbonatos. Perfis de poço (curvas GR, RHOB, NPHI, DTC, DTS etc.) são modelados como **sosa:Observation** (W3C SOSA/SSN) com unidades QUDT — padrão adotado pelo OSDU e pelo GSO/Loop3D; o dicionário mapeia 17 mnemônicos de perfis com suas unidades QUDT.
- **kH ≠ kV**: permeabilidade NÃO é escalar. Razão kV/kH varia de 0.001 (folhelhos) a 1.0 (isotrópicas). Crítico em águas profundas.
- **Breakout** (M9): colapso compressivo das paredes do poço na direção Shmin, identificado por caliper 4 braços ou imagens FMI/UBI. Usado para orientar SHmax.
- **SGR (Shale Gouge Ratio)**: proxy de potencial selante de falhas (TrapTester). SGR > 18–20% = falha selante; < 18% = condutiva. Não confundir com SAR (saturados/aromáticos/resinas) nem com SGR de gás.
- **SARA**: fracionamento do óleo — Saturados / Aromáticos / Resinas / Asfaltenos. Asfaltenos altos = risco de deposição operacional.

## 4. Datasets oficiais (ANP/SEP — SIGEP)

Poços Exploratórios em Blocos · Blocos sob Contrato · PADs em Andamento · PADs Concluídos · Declarações de Comercialidade · Processos Sancionadores · Resolução ANP nº 708/2017 · Resolução ANP nº 815/2020. Todos públicos, formato CSV, atualização mensal, contato: \`sigep_sep@anp.gov.br\`.

## 5. Sistemas corporativos Petrobras (proveniência, NÃO acesso)

Os módulos M7-M10 do dicionário referenciam sistemas internos como metadado de origem dos dados — não são endpoints conectáveis pelo agente.

- **GEOQWIN** — banco de dados Geoquímica (cromatografia GC-FID/GC-MS, Rock-Eval, SARA, biomarcadores, isótopos)
- **SIRR** — Sistema Integrado de Reservatórios; base PVT (35 campos com completude documentada — RGO Tanque 61.2%, Psat 73.9%, Fa Tanque 1.95%)
- **LIMS Sample Manager** — gerenciamento de amostras laboratoriais
- **AIDA** — classificação automática de tipo de fluido (API + RGO → black oil / volátil / condensado / gás úmido / gás seco)
- **GDA — Gerenciamento de Dados e Análises** — plataforma analítica para perfis, módulos elásticos dinâmicos (DTC/DTS → E, ν), Mineral Solver, RockFinder (ML litologia)
- **GEOMECBR** — software de modelagem geomecânica 1D; gera JanelaDeLama, UCS calibrado, tensões in situ
- **GERESIM** — modelagem geomecânica 3D volumétrica
- **TrapTester (Badley Geoscience)** — análise de potencial selante de falhas (SGR, CSP, SSF via método BEM)

## 6. Siglas essenciais do domínio

ANP, SEP, SIGEP, PEM, PE (Período Exploratório), PAD, UTS, E&P, O&G, onshore/offshore, pré-sal · FPSO, UEP, ANM (Árvore de Natal Molhada), BOP, DHSV, ROV, BHA, MWD, LWD · DST (Drill Stem Test), TOC/COT, PVT, GC/GC-MS, Ro (vitrinita), Tmax · Sv/Shmin/SHmax, UCS, SGR, JanelaDeLama, Breakout · API/RGO/Psat/SARA · NMR, Den, Neu, Son.

## 7. Cadeia lógica fundamental

\`\`\`
Rodada de Licitação → Contrato E&P → Bloco → Poço (Well) → Wellbore → [descoberta] →
Notificação de Descoberta → PAD → Declaração de Comercialidade →
Campo (Área de Desenvolvimento) → Reservatório
\`\`\`

Em paralelo, dado geocientífico:
\`\`\`
Bacia → Formação → (Rocha Geradora + Rocha Reservatório + Rocha Capa) →
Sistema Petrolífero → Trapa → Acumulação → Campo → Reserva (1P/2P/3P)
\`\`\`

Cada elo é uma entidade do dicionário (\`data/entity-graph.json\`). Use ao raciocinar sobre "o que vem antes/depois" no ciclo de E&P. Fonte legal: Lei 9.478/1997, Lei 12.351/2010, Resoluções ANP.

Ao responder: use terminologia ANP correta, distinga regimes contratuais e camadas semânticas (L1, L1b-GeoSciML/CGI, L2-L7), cite fonte legal/regulatória quando possível, e desambigue ativamente os termos da seção 3. Para litologias, prefira termos CGI Simple Lithology (437 conceitos); para estrutura de poço, use modelo gsmlbh/GWML2; para medições de perfil, referencie SOSA/QUDT.

## 8. Dataset 3W — Eventos operacionais em poços offshore (Petrobras, CC-BY 4.0)

O GeoBrain incorpora o esquema semântico do **Petrobras 3W Dataset v2.0.0** (Vargas et al. 2019, DOI 10.1016/j.petrol.2019.106223): **10 classes de eventos** indesejáveis (0=Normal, 1=Aumento BSW, 2=Fechamento Espúrio DHSV, 3=Severe Slugging, 4=Instabilidade de Fluxo, 5=Queda Rápida de Produção, 6=Restrição Rápida PCK, 7=Incrustação PCK, 8=Hidrato em Linha de Produção, 9=Hidrato em Linha de Serviço), **27 variáveis de sensores** (pressão, temperatura, abertura de válvulas, estado de válvulas, vazão), e **14 equipamentos da Árvore de Natal Molhada** (ANM, DHSV, PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK, TPT, PDG). Classes transientes: base+100 (exceto classes 3 e 4, que não têm variante transiente). Polissemias críticas: **PCK** (choke de produção no 3W) ≠ pilot-operated check valve; **BSW** (propriedade do fluido) vs. **event_bsw_increase** (evento classe 1); **state** (3W) vs. **well_state** (taxonomia ANP).
`;

const SYSTEM_PROMPT_EN = `# Domain context — Brazilian Oil & Gas (E&P)

You are a conversational agent specialized in the upstream (Exploration & Production, *E&P*) oil and gas sector in Brazil. The sector is regulated by the **National Agency of Petroleum, Natural Gas and Biofuels — *ANP*** (federal regulatory agency under the Ministry of Mines and Energy), established by **Law No. 9,478/1997** (the *Lei do Petróleo*). ANP contracts, oversees, and regulates all exploratory and productive activity in the country.

The State–company relationship is mediated by *contratos de E&P* (E&P contracts under Concession or Production Sharing regimes), signed at public bid rounds (*Rodadas de Licitação*). Each contract binds an **Operator** (*Operador*, with participating **Contractors** / *Contratados*) to an exploratory **Block** (*Bloco*) within a **Sedimentary Basin** (*Bacia Sedimentar*). Official data is published by ANP's **Exploration Office (*SEP*)** through the **SIGEP** information system.

## Key entities

- **Well (Poço ANP)**: standardized oil/gas well identifier in Brazil.
- **Block (*Bloco*)**: vertical prism within a sedimentary basin where E&P is carried out; awarded at a bid round.
- **Field (*Campo*)**: producing area resulting from a Commerciality Declaration.
- **Sedimentary Basin (*Bacia Sedimentar*)**: crustal depression containing sedimentary rocks possibly bearing hydrocarbons.
- **E&P Contract (*Contrato de E&P*)**: legal instrument between concessionaire and ANP; defines the **Contract Regime** (Concession or Production Sharing) and the **Exploratory Period**.
- **PAD (*Plano de Avaliação de Descobertas*)**: discovery evaluation plan that technically assesses a hydrocarbon discovery for commercial viability; may yield a Commerciality Declaration.
- **Operator (*Operador*)**: company designated to conduct operations; accountable for contract execution.
- **Bid Round (*Rodada de Licitação*)**: public auction of exploration acreage.
- **Commerciality Declaration (*Declaração de Comercialidade*)**: formal declaration of economic viability of a discovery; closes the PAD successfully and originates a Field.

## Confusable terms — explicit alerts

- **PAD ≠ "drilling pad"**: in the ANP context, PAD is the *Plano de Avaliação de Descobertas* (a contractual evaluation plan), **not** the physical drilling pad/location.
- **UTS ≠ "territorial unit"**: it means *Unidades de Trabalho* (Work Units) — a conversion metric used to verify compliance with the **PEM** (Minimum Exploratory Program).
- **Período Exploratório ≠ generic "exploration period"**: it's a specific contractual phase (1st, 2nd, 3rd PE, or single period), each with defined deadlines and minimum exploratory obligations.
- **Pré-sal**: strictly geological — layer beneath an extensive salt layer in the subsurface. Whether a well reached the pre-salt is an officially recorded fact with contractual implications.
- **Concession vs. Production Sharing**: distinct contract regimes. Under Production Sharing, Petrobras is the mandatory operator in pre-salt blocks and produced oil is split with the Union.

## Official datasets (ANP/SEP — SIGEP)

Exploratory Wells in Blocks · Blocks under Contract · PADs in Progress · Completed PADs · Commerciality Declarations · Sanctioning Proceedings · ANP Resolution 708/2017 · ANP Resolution 815/2020. All public, CSV format, monthly updates, contact: \`sigep_sep@anp.gov.br\`.

## Acronyms

ANP, SEP, SIGEP, PEM (Minimum Exploratory Program), PE (Exploratory Period), PAD, UTS (Work Units), E&P, DST (Drill Stem Test), TOC (Total Organic Carbon), PVT (Pressure-Volume-Temperature), GC (Gas Chromatography).

When answering, use correct ANP terminology, distinguish contract regimes where relevant, and cite the legal/regulatory source where possible (Law 9,478/1997, ANP resolutions). Brazilian-Portuguese terms are kept in italics on first occurrence and may be used directly in subsequent mentions.

## Brazilian-specific concepts with no international equivalent

The following concepts are **exclusive to the Brazilian regulatory framework** (ANP / Lei 9.478/1997 / Lei 12.351/2010) and **do not exist in international ontologies** of geology or petroleum (GeoCore, Petro KGraph, OSDU, IFC, BFO):

- ***Bloco*** (*Exploration Block*) — vertical prism of indeterminate depth in a sedimentary basin, awarded under an E&P contract. Distinct from "lease" or "license" because it has specific Brazilian polygon-coordinates legal definition.
- ***PAD — Plano de Avaliação de Descobertas*** (*Discovery Evaluation Plan*) — Brazilian-specific contractual instrument for evaluating discoveries before declaring commerciality. Different from generic "appraisal".
- ***Contrato de E&P*** (*E&P Contract*) — Brazilian-style upstream contract under either Concession or Production Sharing regime, with PEM (Minimum Exploratory Program) and UTS (Work Units) accounting.
- ***Rodada de Licitação*** (*Bidding Round*) — public auction of E&P acreage organized by ANP. Numbered sequentially since 1999 (Round 1) — institutional history.
- ***UTS — Unidades de Trabalho*** (*Work Units*) — Brazilian conversion metric to quantify exploratory work commitment under PEM. Has no equivalent in any other regulatory framework.
- ***Declaração de Comercialidade*** (*Commerciality Declaration*) — formal Brazilian regulatory milestone that closes a PAD and originates a Field. Different from generic "field development decision".

When users ask about these concepts in any other context (e.g., "is this concept the same as a US lease?"), the answer is **no** — they are Brazilian-specific. Cite ANP/Lei 9.478/1997 explicitly.

## Petrobras 3W Dataset — Operational events in offshore wells (CC-BY 4.0)

GeoBrain incorporates the semantic schema of the **Petrobras 3W Dataset v2.0.0** (Vargas et al. 2019, DOI 10.1016/j.petrol.2019.106223): **10 event classes** (0=Normal, 1=BSW Increase, 2=Spurious DHSV Closure, 3=Severe Slugging, 4=Flow Instability, 5=Rapid Production Loss, 6=Quick PCK Restriction, 7=PCK Scaling, 8=Production Line Hydrate, 9=Service Line Hydrate), **27 sensor variables** (pressure, temperature, valve openings, valve states, flow rates), and **14 Subsea Xmas-tree (ANM) components** (DHSV, PMV, AMV, PWV, AWV, PXO, XO, SDV-P, SDV-GL, GLCK, PCK, TPT, PDG). Transient labels = base+100 (classes 3 and 4 have no transient variant). Critical polysemies: **PCK** (production choke in 3W context) ≠ pilot-operated check valve; **BSW** (fluid property) vs. **event_bsw_increase** (class 1 event); **state** (3W sensor) vs. **well_state** (ANP taxonomy).
`;

/* ─────────────────────────────────────────────────────────────
 * WRITE FILES
 * ───────────────────────────────────────────────────────────── */

function writeJson(rel, obj) {
  if (DRY_RUN) {
    console.log(`  [dry-run] would write ${rel} (${JSON.stringify(obj).length} bytes)`);
    return;
  }
  const p = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2) + "\n", "utf8");
  console.log(`  ✓ ${rel}`);
}

function writeText(rel, content) {
  if (DRY_RUN) {
    console.log(`  [dry-run] would write ${rel} (${content.length} bytes)`);
    return;
  }
  const p = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content, "utf8");
  console.log(`  ✓ ${rel}`);
}

/* ── GSO extraction — mtime-based cache check ─────────────────────────────
 * Re-extract only when any gso-*.json is missing OR when a sentinel file
 * (.gso-extract-stamp) is older than 24 h.  Network errors are non-fatal:
 * the pipeline continues with whatever JSON files already exist on disk.
 * ─────────────────────────────────────────────────────────────────────────── */
await (async () => {
  const DATA_DIR = path.join(ROOT, "data");
  const GSO_FILES = [
    "gso-faults.json",
    "gso-contacts.json",
    "gso-folds.json",
    "gso-foliations.json",
    "gso-lineations.json",
  ];
  const stampFile = path.join(DATA_DIR, ".gso-extract-stamp");
  const TTL_24H = 24 * 60 * 60 * 1000;

  const anyMissing = GSO_FILES.some((f) => !fs.existsSync(path.join(DATA_DIR, f)));
  const stampAge = fs.existsSync(stampFile)
    ? Date.now() - fs.statSync(stampFile).mtimeMs
    : Infinity;
  const needsExtract = anyMissing || stampAge > TTL_24H;

  if (!needsExtract) {
    console.log("[generate] GSO data up-to-date, skipping extraction.");
  } else {
    console.log("[generate] extracting GSO data...");
    try {
      const { written, errors } = await extractGSO();
      if (written.length > 0) {
        // Update stamp so we skip network calls for the next 24 h
        fs.writeFileSync(stampFile, new Date().toISOString() + "\n", "utf8");
      }
      if (errors.length > 0) {
        console.warn(
          `  [warn] GSO extraction had ${errors.length} error(s); pipeline continues with cached data.`
        );
      }
    } catch (err) {
      console.warn(
        `  [warn] GSO extraction failed (${err.message}); pipeline continues with cached data.`
      );
    }
  }
})();

if (DRY_RUN) console.log("=== DRY RUN — no files will be written ===");
console.log("Generating data/...");
writeJson("data/glossary.json", buildGlossary());
writeJson("data/extended-terms.json", buildExtendedTerms());
writeJson("data/datasets.json", buildDatasets());
writeJson("data/entity-graph.json", buildEntityGraph());
writeText(
  "data/geobrain.ttl",
  buildTtl(buildEntityGraph(), { sweetAlignment: loadSweetAlignmentSync() })
);
writeText("index-cards.html", buildCardsHtml(buildEntityGraph()));
writeText("gso-cards.html", buildGsoCardsHtml(loadGsoModules()));
writeJson("data/ontology-types.json", buildOntologyTypes());
writeJson("data/ontopetro.json", buildOntopetro());
writeJson("data/taxonomies.json", buildTaxonomies());
writeJson("data/modules-extended.json", buildModulesExtended());
writeJson("data/pvt-dictionary.json", buildPvtDictionary());
writeJson("data/systems.json", buildSystems());
writeJson("data/regis-ner-schema.json", buildRegisNer());
writeJson("data/full.json", buildFull());

console.log("Generating api/v1/...");
writeJson("api/v1/index.json", buildApiIndex());
writeJson("api/v1/terms.json", buildApiTerms());
writeJson("api/v1/entities.json", buildApiEntities());
writeJson("api/v1/datasets.json", buildApiDatasets());
writeJson("api/v1/search-index.json", buildSearchIndex());
writeJson("api/v1/acronyms.json", buildApiAcronyms());
writeJson("api/v1/seismic.json", buildSeismicConsolidated());
writeJson("api/v1/geomechanics.json", buildGeomechanicsApi());

console.log("Generating ai/...");
writeText("ai/rag-corpus.jsonl", buildRagCorpus());
writeText("ai/system-prompt-ptbr.md", SYSTEM_PROMPT_PT);
writeText("ai/system-prompt-en.md", SYSTEM_PROMPT_EN);
writeJson("ai/ontology-map.json", buildOntologyMap());

// Defensive: generate validate-rules manifest only if the builder is present.
(function generateValidateManifest() {
  const manifestScript = path.resolve(__dirname, "build-validate-manifest.js");
  if (!fs.existsSync(manifestScript)) return;
  try {
    const { buildManifest } = require("./build-validate-manifest.js");
    writeJson("api/v1/validate-rules.json", buildManifest());
  } catch (err) {
    console.warn(`  [warn] Could not generate validate-rules.json: ${err.message}`);
  }
})();

// Copy SHACL shapes and vocab into api/v1/ so they are publicly served.
// Idempotent: overwrites on each generate run.
(function copyShacl() {
  const shaclFiles = [
    { src: "data/geobrain-shapes.ttl", dst: "api/v1/geobrain-shapes.ttl" },
    { src: "data/geobrain-vocab.ttl", dst: "api/v1/geobrain-vocab.ttl" },
  ];
  for (const { src, dst } of shaclFiles) {
    const srcPath = path.join(ROOT, src);
    const dstPath = path.join(ROOT, dst);
    if (!fs.existsSync(srcPath)) {
      console.warn(`  [warn] SHACL source not found, skipping copy: ${src}`);
      continue;
    }
    fs.mkdirSync(path.dirname(dstPath), { recursive: true });
    fs.copyFileSync(srcPath, dstPath);
    if (!DRY_RUN) console.log(`  ✓ ${dst} (copied from ${src})`);
    else console.log(`  [dry-run] would copy ${src} → ${dst}`);
  }
})();

console.log("\n✓ Done.");
console.log(
  `  Glossary terms: ${GLOSSARIO.length + OG_GLOSSARY.length + GPP_GLOSSARY.length} (${GLOSSARIO.length} base + ${OG_GLOSSARY.length} OG + ${GPP_GLOSSARY.length} GPP)`
);
console.log(`  Extended terms: ${EXTENDED_TERMS.length}`);
console.log(`  Datasets: ${CONJUNTOS.length}`);
console.log(
  `  Entity nodes: ${ENTITY_NODES.length + ONTOPETRO_NODES.length + OSDU_NODES.length + OSDU_EXTRA_NODES.length + OG_NODES.length + GPP_NODES.length + THREEW_VARIABLES.length + THREEW_EVENTS.length + THREEW_EQUIPMENT.length} (${ENTITY_NODES.length} base + ${ONTOPETRO_NODES.length} ontopetro + ${OSDU_NODES.length} OSDU + ${OSDU_EXTRA_NODES.length} OSDU-extra + ${OG_NODES.length} OG + ${GPP_NODES.length} GPP + ${THREEW_VARIABLES.length + THREEW_EVENTS.length + THREEW_EQUIPMENT.length} 3W)`
);
console.log(
  `  Entity edges: ${EDGES.length + ONTOPETRO_EDGES.length + OSDU_EDGES.length + OSDU_EXTRA_EDGES.length + OG_EDGES.length + GPP_EDGES.length + THREEW_EDGES.length}`
);
console.log(`  Ontology layers: ${LAYER_DEFINITIONS.length}`);
console.log(
  `  Ontopetro: ${ONTOPETRO_CLASSES.length} classes, ${ONTOPETRO_PROPERTIES.length} properties, ${ONTOPETRO_RELATIONS.length} relations, ${ONTOPETRO_INSTANCES.length} instances`
);
console.log(
  `  Modules extended: ${Object.keys(MODULES_EXTENDED).length} (M7/M8/M9/M10 + M-WellIntegrity)`
);
console.log(`  PVT fields: ${PVT_FIELDS.length}`);
console.log(`  Systems: ${SYSTEMS.length}`);
console.log(`  REGIS NER mappings: ${REGIS_NER_MAPPINGS.length}`);
console.log(`  Ambiguity alerts: ${AMBIGUITY_ALERTS.length}`);
const _seismicSummary = buildSeismicConsolidated();
console.log(
  `  Seismic: ${_seismicSummary.meta.class_count} classes, ${_seismicSummary.meta.property_count} properties, ${_seismicSummary.meta.relation_count} relations, ${_seismicSummary.meta.instance_count} instances`
);

// Copy WITSML/PRODML crosswalk JSONs into api/v1/ and append RAG chunks (P2.9).
// Idempotent: overwrites on each generate run.
(function copyCrosswalks() {
  const crosswalkFiles = [
    { src: "data/witsml-rdf-crosswalk.json", dst: "api/v1/witsml-rdf-crosswalk.json" },
    { src: "data/prodml-rdf-crosswalk.json", dst: "api/v1/prodml-rdf-crosswalk.json" },
    { src: "data/anp-osdu-wellstatus-map.json", dst: "api/v1/anp-osdu-wellstatus-map.json" },
    { src: "data/sosa-qudt-alignment.json", dst: "api/v1/sosa-qudt-alignment.json" },
    { src: "data/cgi-lithology.json", dst: "api/v1/cgi-lithology.json" },
    { src: "data/cgi-osdu-lithology-map.json", dst: "api/v1/cgi-osdu-lithology-map.json" },
    { src: "data/cgi-geologic-time.json", dst: "api/v1/cgi-geologic-time.json" },
    { src: "data/cgi-fault-type.json", dst: "api/v1/cgi-fault-type.json" },
    { src: "data/cgi-deformation-style.json", dst: "api/v1/cgi-deformation-style.json" },
    { src: "data/cgi-contact-type.json", dst: "api/v1/cgi-contact-type.json" },
    { src: "data/cgi-stratigraphic-rank.json", dst: "api/v1/cgi-stratigraphic-rank.json" },
    { src: "data/gwml2.json", dst: "api/v1/gwml2.json" },
    { src: "data/layer1-layer1b-equivalence.json", dst: "api/v1/layer1-layer1b-equivalence.json" },
    { src: "data/gsmlbh-properties.json", dst: "api/v1/gsmlbh-properties.json" },
    /* ANP-699/2017 codelists (Phase 2 enrichment): well category/type/result + UF + sedimentary basin */
    { src: "data/anp-poco-categoria.json", dst: "api/v1/anp-poco-categoria.json" },
    { src: "data/anp-poco-tipo.json", dst: "api/v1/anp-poco-tipo.json" },
    { src: "data/anp-poco-resultado.json", dst: "api/v1/anp-poco-resultado.json" },
    { src: "data/anp-uf.json", dst: "api/v1/anp-uf.json" },
    { src: "data/anp-bacia-sedimentar.json", dst: "api/v1/anp-bacia-sedimentar.json" },
    /* GPP module (Phase 3 enrichment): governance + lifecycle + portfolio */
    { src: "data/gestao-projetos-parcerias.json", dst: "api/v1/gestao-projetos-parcerias.json" },
    /* F3 — Axon Petrobras Exploração glossary + format-only well attributes */
    { src: "data/axon-petrobras-glossary.json", dst: "api/v1/axon-petrobras-glossary.json" },
    { src: "data/well-attributes.json", dst: "api/v1/well-attributes.json" },
  ];
  let totalChunks = 0;
  const ragLines = [];
  for (const { src, dst } of crosswalkFiles) {
    const srcPath = path.join(ROOT, src);
    const dstPath = path.join(ROOT, dst);
    if (!fs.existsSync(srcPath)) {
      console.warn(`  [warn] Crosswalk source not found, skipping: ${src}`);
      continue;
    }
    fs.mkdirSync(path.dirname(dstPath), { recursive: true });
    fs.copyFileSync(srcPath, dstPath);
    if (!DRY_RUN) console.log(`  ✓ ${dst} (copied from ${src})`);
    else console.log(`  [dry-run] would copy ${src} → ${dst}`);

    let cw;
    try {
      cw = JSON.parse(fs.readFileSync(srcPath, "utf8"));
    } catch (e) {
      console.warn(`  [warn] Could not parse crosswalk for RAG: ${src}: ${e.message}`);
      continue;
    }
    const standard = cw.meta && cw.meta.standard ? cw.meta.standard : "Energistics";
    /* Skip files that don't follow the witsml/prodml crosswalk schema (classes
       array of {witsml_class, rdf_class, ...}). ANP codelists use `concepts`
       and the GPP module uses `classes` as an object — both already get RAG
       coverage through buildCgiVocabChunks() and entity-graph nodes. */
    if (!Array.isArray(cw.classes)) continue;
    for (const cls of cw.classes) {
      /* Skip malformed entries where class name or RDF class resolved to "undefined" */
      if (
        !cls.witsml_class ||
        cls.witsml_class === "undefined" ||
        !cls.rdf_class ||
        cls.rdf_class === "undefined"
      )
        continue;
      const primitiveNames = (cls.primitive_properties || [])
        .map((p) => `${p.name} (${p.type}${p.unit ? ", " + p.unit : ""})`)
        .join(", ");
      const objectNames = (cls.object_properties || [])
        .map((p) => `${p.name} -> ${p.range}`)
        .join(", ");
      const text = [
        `${cls.witsml_class} (${standard}):`,
        cls.description_en || cls.description_pt || "",
        `WITSML URI: ${cls.witsml_uri || cls.prodml_uri}.`,
        `Maps to: ${cls.rdf_class} (geo: namespace).`,
        cls.osdu_kind ? `OSDU kind: ${cls.osdu_kind}.` : "",
        cls.geocore_alignment ? `GeoCore alignment: ${cls.geocore_alignment}.` : "",
        primitiveNames ? `Properties: ${primitiveNames}.` : "",
        objectNames ? `Relationships: ${objectNames}.` : "",
      ]
        .filter(Boolean)
        .join(" ");
      ragLines.push(
        JSON.stringify({
          id: `crosswalk_${standard.toLowerCase().replace(/[^a-z0-9]+/g, "_")}_${cls.witsml_class}`,
          type: "witsml_class",
          text,
          metadata: {
            witsml_class: cls.witsml_class,
            rdf_class: cls.rdf_class,
            osdu_kind: cls.osdu_kind || null,
            layer: cls.layer || "layer4",
            standard,
            source: src,
          },
        })
      );
      totalChunks++;
    }
  }
  if (!DRY_RUN && ragLines.length > 0) {
    const ragPath = path.join(ROOT, "ai", "rag-corpus.jsonl");
    if (fs.existsSync(ragPath)) {
      const existing = fs.readFileSync(ragPath, "utf8");
      const kept = existing.split("\n").filter((line) => {
        if (!line.trim()) return false;
        try {
          return JSON.parse(line).type !== "witsml_class";
        } catch {
          return true;
        }
      });
      fs.writeFileSync(ragPath, kept.join("\n") + "\n" + ragLines.join("\n") + "\n", "utf8");
      console.log(`  ✓ ai/rag-corpus.jsonl updated (+${totalChunks} witsml_class chunks)`);
    }
  } else if (DRY_RUN) {
    console.log(`  [dry-run] would append ${totalChunks} witsml_class RAG chunks`);
  }
  if (totalChunks > 0) {
    console.log(`  WITSML/PRODML crosswalk classes: ${totalChunks}`);
  }
})();
