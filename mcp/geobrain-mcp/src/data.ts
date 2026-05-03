/**
 * data.ts — loads all static JSON once at startup and caches in memory.
 *
 * The server resolves data paths relative to this file's location so the
 * binary can be run from any working directory.
 */

import { readFileSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
// At runtime the compiled JS lives at dist/data.js.
// dist/ -> geolytics-mcp/ -> mcp/ -> repo root  (3 levels up)
const REPO_ROOT = resolve(__dirname, "../../..");

function loadJson<T>(relPath: string): T {
  const abs = resolve(REPO_ROOT, relPath);
  if (!existsSync(abs)) {
    throw new Error(`Data file not found: ${abs}`);
  }
  return JSON.parse(readFileSync(abs, "utf-8")) as T;
}

function loadJsonlLines(relPath: string): Record<string, unknown>[] {
  const abs = resolve(REPO_ROOT, relPath);
  if (!existsSync(abs)) return [];
  return readFileSync(abs, "utf-8")
    .split("\n")
    .filter((l) => l.trim())
    .map((l) => JSON.parse(l) as Record<string, unknown>);
}

// ---------- type shapes (just enough to satisfy TypeScript) ----------

export interface GlossaryTerm {
  id: string;
  termo: string;
  termo_en?: string;
  categoria?: string;
  definicao?: string;
  legal_source?: string;
  fonte?: string;
  apareceEm?: string[];
  petrokgraph_uri?: string;
  osdu_kind?: string | null;
  geosciml_uri?: string;
  geocoverage?: string[];
  synonyms_pt?: string[];
  synonyms_en?: string[];
  examples?: string[];
  [key: string]: unknown;
}

export interface ExtendedTerm extends GlossaryTerm {
  legal_source?: string;
}

export interface Acronym {
  id: string;
  sigla: string;
  expansion_pt?: string;
  expansion_en?: string;
  category?: string;
  it_generic?: boolean;
  disambiguation?: string;
  [key: string]: unknown;
}

export interface EntityNode {
  id: string;
  label?: string;
  label_en?: string;
  type?: string;
  definition?: string;
  definition_en_canonical?: string;
  petrokgraph_uri?: string;
  osdu_kind?: string | null;
  geosciml_uri?: string;
  gso_uri?: string;
  owl_uri?: string;
  geocoverage?: string[];
  [key: string]: unknown;
}

export interface EntityEdge {
  source: string;
  target: string;
  relation: string;
  relation_label_pt?: string;
  relation_label_en?: string;
  style?: string;
}

export interface EntityGraph {
  nodes: EntityNode[];
  edges: EntityEdge[];
}

export interface OntopetroClass {
  id: string;
  name: string;
  name_en?: string;
  superclass?: string;
  description?: string;
  domain?: string;
  sources?: string[];
  entity_graph_id?: string;
}

export interface OntologyLayer {
  id: string;
  name: string;
  maintainer?: string;
  type?: string;
  description?: string;
  concepts_count?: number;
  language?: string;
  geolytics_coverage?: string[];
  [key: string]: unknown;
}

export interface RagChunk {
  id: string;
  type: string;
  text: string;
  metadata?: Record<string, unknown>;
}

export interface CgiLithologyConcept {
  id: string;
  label_en: string;
  label_pt?: string;
  parents?: string[];
  definition_en?: string;
  uri?: string;
  [key: string]: unknown;
}

export interface CgiGeologicTimeUnit {
  id: string;
  rank: string;
  label_en: string;
  label_pt?: string;
  start_ma?: number;
  end_ma?: number;
  parent?: string | null;
  brazil_notes?: string;
  uri?: string;
}

// ---------- loaded data (singleton) ----------

let _loaded = false;

export let glossaryTerms: GlossaryTerm[] = [];
export let extendedTerms: ExtendedTerm[] = [];
export let acronyms: Acronym[] = [];
export let entityGraph: EntityGraph = { nodes: [], edges: [] };
export let ontopetroClasses: OntopetroClass[] = [];
export let ontologyLayers: OntologyLayer[] = [];
export let ragChunks: RagChunk[] = [];

// Eagerly loaded at module evaluation time so tools can import them directly.
export const cgiLithology: CgiLithologyConcept[] = (() => {
  const data = loadJson<{ meta: unknown; concepts?: CgiLithologyConcept[] }>(
    "data/cgi-lithology.json"
  );
  return data.concepts ?? [];
})();

export const cgiGeologicTime: CgiGeologicTimeUnit[] = (() => {
  const data = loadJson<{ units: CgiGeologicTimeUnit[] }>("data/cgi-geologic-time.json");
  return data.units ?? [];
})();

export function loadAll(): void {
  if (_loaded) return;

  const glossary = loadJson<{ terms: GlossaryTerm[] }>("data/glossary.json");
  glossaryTerms = glossary.terms ?? [];

  const extended = loadJson<{ terms: ExtendedTerm[] }>("data/extended-terms.json");
  extendedTerms = extended.terms ?? [];

  const acr = loadJson<{ acronyms: Acronym[] }>("data/acronyms.json");
  acronyms = acr.acronyms ?? [];

  entityGraph = loadJson<EntityGraph>("data/entity-graph.json");

  const onto = loadJson<{ classes?: OntopetroClass[] }>("data/ontopetro.json");
  ontopetroClasses = onto.classes ?? [];

  const ontMap = loadJson<{ layers?: OntologyLayer[] }>("ai/ontology-map.json");
  ontologyLayers = ontMap.layers ?? [];

  const rawChunks = loadJsonlLines("ai/rag-corpus.jsonl");
  ragChunks = rawChunks as unknown as RagChunk[];

  _loaded = true;
}
