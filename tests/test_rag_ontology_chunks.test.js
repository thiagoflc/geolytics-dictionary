/**
 * tests/test_rag_ontology_chunks.test.js — Snapshot tests para os chunks
 * `ontology_concept` emitidos por `emitOntologyConceptChunks()` (F8) em
 * ai/rag-corpus.jsonl.
 *
 * Detecta drift entre o RAG corpus e o entity-graph: cada referência a
 * `metadata.entities[*]` deve resolver a um id real em data/entity-graph.json.
 *
 * Cobre:
 *   1. Total de chunks ontology_concept = 26.
 *   2. Schema obrigatório (id, type, text, metadata.subcategory) presente.
 *   3. Distribuição por subcategoria bate com a especificação F8.
 *   4. Todos os IDs de entidade referenciados existem no entity-graph.
 *   5. Texto de cada chunk tem >= 100 chars (sanity).
 *   6. IDs únicos entre todos os chunks ontology_concept.
 *
 * Run: node --test tests/test_rag_ontology_chunks.test.js
 */

import { test, describe, before } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const RAG_CORPUS = path.join(REPO_ROOT, "ai", "rag-corpus.jsonl");
const ENTITY_GRAPH = path.join(REPO_ROOT, "data", "entity-graph.json");

const EXPECTED_TOTAL = 26;
const EXPECTED_SUBCATEGORY_COUNTS = {
  golden_rule: 1,
  ontology_layer: 6,
  auxiliary_role: 5,
  bridge: 7,
  predicate_vocabulary: 4,
  project_metric: 3,
};
const VALID_SUBCATEGORIES = new Set(Object.keys(EXPECTED_SUBCATEGORY_COUNTS));

const MIN_TEXT_CHARS = 100;

/* Lazy-loaded shared state (carregado uma vez no `before`). */
let chunks = [];
let entityIds = new Set();

before(() => {
  /* Lê todas as linhas JSONL e filtra ontology_concept. */
  const raw = fs.readFileSync(RAG_CORPUS, "utf8");
  for (const line of raw.split("\n")) {
    if (!line.trim()) continue;
    let obj;
    try {
      obj = JSON.parse(line);
    } catch {
      continue;
    }
    if (obj.type === "ontology_concept") chunks.push(obj);
  }

  const eg = JSON.parse(fs.readFileSync(ENTITY_GRAPH, "utf8"));
  for (const node of eg.nodes || []) {
    if (node.id) entityIds.add(node.id);
  }
});

/* ───────────────────────────────────────────────────────────────
 * 1. Corpus has 26 ontology_concept chunks.
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept chunk inventory", () => {
  test(`corpus contains exactly ${EXPECTED_TOTAL} ontology_concept chunks`, () => {
    assert.equal(
      chunks.length,
      EXPECTED_TOTAL,
      `expected ${EXPECTED_TOTAL} ontology_concept chunks, found ${chunks.length}`
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 2. Required schema fields.
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept chunk schema", () => {
  test("each chunk has id, type, text, metadata.subcategory", () => {
    for (const c of chunks) {
      assert.ok(typeof c.id === "string" && c.id.length > 0, `chunk missing id: ${JSON.stringify(c).slice(0, 80)}`);
      assert.equal(c.type, "ontology_concept", `wrong type on ${c.id}`);
      assert.ok(typeof c.text === "string" && c.text.length > 0, `chunk ${c.id} missing text`);
      assert.ok(c.metadata && typeof c.metadata === "object", `chunk ${c.id} missing metadata`);
      assert.ok(
        typeof c.metadata.subcategory === "string",
        `chunk ${c.id} missing metadata.subcategory`
      );
    }
  });

  test("each subcategory is in the canonical set", () => {
    for (const c of chunks) {
      assert.ok(
        VALID_SUBCATEGORIES.has(c.metadata.subcategory),
        `chunk ${c.id} has unknown subcategory "${c.metadata.subcategory}"`
      );
    }
  });
});

/* ───────────────────────────────────────────────────────────────
 * 3. Subcategory counts match spec.
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept subcategory distribution", () => {
  test("counts per subcategory match spec (1+6+5+7+4+3 = 26)", () => {
    const counts = {};
    for (const c of chunks) {
      counts[c.metadata.subcategory] = (counts[c.metadata.subcategory] || 0) + 1;
    }
    for (const [sub, expected] of Object.entries(EXPECTED_SUBCATEGORY_COUNTS)) {
      assert.equal(
        counts[sub],
        expected,
        `subcategory "${sub}": expected ${expected}, got ${counts[sub] || 0}`
      );
    }
  });
});

/* ───────────────────────────────────────────────────────────────
 * 4. Every entity referenced exists in the entity-graph.
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept entity references", () => {
  test("each metadata.entities[*] resolves to a node in entity-graph.json", () => {
    const dangling = [];
    for (const c of chunks) {
      const entities = Array.isArray(c.metadata.entities) ? c.metadata.entities : [];
      for (const eid of entities) {
        if (!entityIds.has(eid)) {
          dangling.push({ chunk: c.id, entity: eid });
        }
      }
    }
    assert.equal(
      dangling.length,
      0,
      `dangling entity references (RAG references ids that do not exist in entity-graph.json):\n` +
        dangling.map((d) => `  chunk=${d.chunk} entity=${d.entity}`).join("\n")
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 5. Chunk text non-empty (>= 100 chars sanity bound).
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept text length", () => {
  test(`each chunk text has >= ${MIN_TEXT_CHARS} chars`, () => {
    const tooShort = chunks.filter((c) => c.text.length < MIN_TEXT_CHARS);
    assert.equal(
      tooShort.length,
      0,
      `chunks below ${MIN_TEXT_CHARS} chars (likely a schema regression):\n` +
        tooShort.map((c) => `  ${c.id}: ${c.text.length} chars`).join("\n")
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 6. Unique chunk IDs.
 * ─────────────────────────────────────────────────────────────── */

describe("ontology_concept id uniqueness", () => {
  test("no two ontology_concept chunks share an id", () => {
    const seen = new Map();
    const dups = [];
    for (const c of chunks) {
      if (seen.has(c.id)) dups.push(c.id);
      else seen.set(c.id, true);
    }
    assert.equal(
      dups.length,
      0,
      `duplicate ontology_concept ids: ${dups.join(", ")}`
    );
  });
});
