// TTL (Turtle/RDF) serializer for the Geolytics entity-graph.
// Pure transformation: takes { nodes, edges } and returns a Turtle string.
//
// Prefixes:
//   geo:   https://geolytics.petrobras.com.br/dict/
//   osdu:  https://w3id.org/osdu#
//   kg:    https://raw.githubusercontent.com/Petroles/PetroNLP/main/Petro%20KGraph%20public.owl#
//   skos:  http://www.w3.org/2004/02/skos/core#
//   rdfs:  http://www.w3.org/2000/01/rdf-schema#
//   owl:   http://www.w3.org/2002/07/owl#
//   xsd:   http://www.w3.org/2001/XMLSchema#

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const PREFIXES = [
  ["geo", "https://geolytics.petrobras.com.br/dict/"],
  ["osdu", "https://w3id.org/osdu#"],
  ["kg", "https://raw.githubusercontent.com/Petroles/PetroNLP/main/Petro%20KGraph%20public.owl#"],
  ["skos", "http://www.w3.org/2004/02/skos/core#"],
  ["rdfs", "http://www.w3.org/2000/01/rdf-schema#"],
  ["owl", "http://www.w3.org/2002/07/owl#"],
  ["xsd", "http://www.w3.org/2001/XMLSchema#"],
  ["sweet", "http://sweetontology.net/"],
  ["geocore", "http://loop3d.org/GKO/geocore#"],
  ["gsmlb", "http://geosciml.org/def/gsmlb#"],
  ["gsmlbh", "http://geosciml.org/def/gsmlbh#"],
  ["cgi", "http://resource.geosciml.org/classifier/cgi/lithOntology/"],
];

// Load SWEET alignment data from data/sweet-alignment.json.
// Returns a Map: geolytics_id -> alignment record(s) (array).
// Optional — gracefully returns empty Map if file is absent.
async function loadSweetAlignment() {
  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const candidate = path.join(here, "..", "data", "sweet-alignment.json");
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

// Load layer1-layer1b equivalence mappings from data/layer1-layer1b-equivalence.json.
// Returns the parsed object or null if the file is absent.
function loadLayer1Layer1bEquivalence() {
  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const candidate = path.join(here, "..", "data", "layer1-layer1b-equivalence.json");
    if (!fs.existsSync(candidate)) return null;
    return JSON.parse(fs.readFileSync(candidate, "utf8"));
  } catch {
    return null;
  }
}

// Try to load OSDU_CANONICAL from a sibling file at runtime.
// Optional — if missing, we fall back to deriving the type slot from the kind.
async function loadOsduCanonical() {
  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const candidate = path.join(here, "osdu-canonical.js");
    if (!fs.existsSync(candidate)) return null;
    const mod = await import(candidate);
    return mod.OSDU_CANONICAL || mod.default?.OSDU_CANONICAL || null;
  } catch {
    return null;
  }
}

// Best-effort kind → w3id URI:
// Pattern: "<partition>:<src>:master-data--Well:1.0.0" → "https://w3id.org/osdu#Well"
// Falls back to null if the kind doesn't match.
export function osduKindToUri(kind, canonical = null) {
  if (!kind || typeof kind !== "string") return null;
  if (canonical && canonical[kind] && canonical[kind].owl_uri) {
    return canonical[kind].owl_uri;
  }
  const m = kind.match(
    /(?:master-data|reference-data|work-product-component|work-product|dataset)--([A-Za-z0-9_]+)/
  );
  if (!m) return null;
  return `https://w3id.org/osdu#${m[1]}`;
}

// Escape a literal for a regular Turtle short string ("...").
function escShort(s) {
  return String(s)
    .replace(/\\/g, "\\\\")
    .replace(/"/g, '\\"')
    .replace(/\n/g, "\\n")
    .replace(/\r/g, "\\r")
    .replace(/\t/g, "\\t");
}

// Escape for Turtle long string ("""...""").
// Long strings allow bare newlines; we only need to escape a literal triple-quote
// and trailing backslashes.
function escLong(s) {
  return String(s).replace(/\\/g, "\\\\").replace(/"""/g, '\\"\\"\\"');
}

function lit(value, lang) {
  if (value == null) return null;
  const str = String(value);
  const isMultiLine = /[\r\n]/.test(str) || str.length > 120;
  const body = isMultiLine ? `"""${escLong(str)}"""` : `"${escShort(str)}"`;
  return lang ? `${body}@${lang}` : body;
}

function uriRef(absoluteUri) {
  // Wrap an absolute URI as a Turtle <...> ref. Encode the few chars that break parsing.
  const safe = String(absoluteUri).replace(/[<>"`{}\\^|\s]/g, encodeURIComponent);
  return `<${safe}>`;
}

// Local-name validation: keep things simple — only allow chars safely usable
// in a Turtle PNAME_LN local part without escapes (letters, digits, hyphen, underscore, dot).
// Hyphens are valid; we still sanitize anything stray.
function safeLocal(id) {
  return String(id).replace(/[^A-Za-z0-9_\-.]/g, "_");
}

function geoRef(id) {
  return `geo:${safeLocal(id)}`;
}

function indent(s, n = 4) {
  const pad = " ".repeat(n);
  return s
    .split("\n")
    .map((line) => (line.length ? pad + line : line))
    .join("\n");
}

// --- Main builder ----------------------------------------------------------

export function buildTtl(graph, options = {}) {
  const nodes = Array.isArray(graph?.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph?.edges) ? graph.edges : [];
  const canonical = options.osduCanonical || null;
  // sweetAlignment: Map<geolytics_id, alignment[]>  (optional)
  const sweetAlignment = options.sweetAlignment instanceof Map ? options.sweetAlignment : new Map();

  const out = [];

  // Prefixes
  for (const [p, uri] of PREFIXES) {
    out.push(`@prefix ${p}: <${uri}> .`);
  }
  out.push("");

  // Header comment
  out.push("# Geolytics dictionary — entity graph (Turtle serialization)");
  out.push(`# Generated: ${new Date().toISOString()}`);
  out.push(`# Nodes: ${nodes.length}  Edges: ${edges.length}`);
  out.push("");

  // ---- Classes (one owl:Class per node) ----
  out.push("#");
  out.push("# Classes");
  out.push("#");
  out.push("");

  for (const node of nodes) {
    if (!node || !node.id) continue;
    const subj = geoRef(node.id);
    const lines = [`${subj} a owl:Class ;`];
    const preds = [];

    if (node.label) {
      preds.push(`skos:prefLabel ${lit(node.label, "pt")}`);
    }
    if (node.label_en) {
      preds.push(`skos:prefLabel ${lit(node.label_en, "en")}`);
    }
    if (node.type) {
      preds.push(`geo:entityType ${lit(node.type)}`);
    }

    // altLabels (synonyms)
    const synPt = Array.isArray(node.synonyms_pt) ? node.synonyms_pt : [];
    const synEn = Array.isArray(node.synonyms_en) ? node.synonyms_en : [];
    for (const s of synPt) {
      if (s) preds.push(`skos:altLabel ${lit(s, "pt")}`);
    }
    for (const s of synEn) {
      if (s) preds.push(`skos:altLabel ${lit(s, "en")}`);
    }

    if (node.definition) {
      preds.push(`skos:definition ${lit(node.definition, "pt")}`);
    }

    const examples = Array.isArray(node.examples) ? node.examples : [];
    for (const ex of examples) {
      if (ex != null && ex !== "") preds.push(`skos:example ${lit(ex)}`);
    }

    // owl:sameAs → OSDU class URI
    const osduUri = osduKindToUri(node.osdu_kind, canonical);
    if (osduUri) {
      preds.push(`owl:sameAs ${uriRef(osduUri)}`);
    }

    // rdfs:seeAlso → Petro KGraph URI
    if (node.petrokgraph_uri) {
      preds.push(`rdfs:seeAlso ${uriRef(node.petrokgraph_uri)}`);
    }

    // SWEET alignment triples (skos:exactMatch / closeMatch / broadMatch / narrowMatch / relatedMatch)
    const sweetEntries = sweetAlignment.get(node.id) || [];
    for (const sa of sweetEntries) {
      const predicate = sa.alignment_type || "skos:relatedMatch";
      // predicate is expected as "skos:exactMatch" etc. — emit as-is (valid SKOS property)
      const uris = Array.isArray(sa.sweet_uris) ? sa.sweet_uris : [];
      for (const uri of uris) {
        preds.push(`${predicate} ${uriRef(uri)}`);
      }
    }

    // geo:geocoverage (multi-valued)
    const geocoverage = Array.isArray(node.geocoverage) ? node.geocoverage : [];
    for (const g of geocoverage) {
      if (g) preds.push(`geo:geocoverage ${lit(g)}`);
    }

    if (preds.length === 0) {
      // No predicates beyond rdf:type — close cleanly.
      lines[0] = `${subj} a owl:Class .`;
    } else {
      const body = preds.map((p, i) => `${p}${i === preds.length - 1 ? " ." : " ;"}`).join("\n");
      lines.push(indent(body, 4));
    }

    out.push(lines.join("\n"));
    out.push("");
  }

  // ---- Object properties (one per distinct relation) ----
  out.push("#");
  out.push("# Object properties");
  out.push("#");
  out.push("");

  // Aggregate per-relation domain / range / labels.
  const relations = new Map();
  for (const e of edges) {
    if (!e || !e.relation) continue;
    const key = e.relation;
    let r = relations.get(key);
    if (!r) {
      r = {
        relation: key,
        label_pt: e.relation_label_pt || null,
        label_en: e.relation_label_en || null,
        domains: new Set(),
        ranges: new Set(),
      };
      relations.set(key, r);
    }
    if (e.source) r.domains.add(e.source);
    if (e.target) r.ranges.add(e.target);
    // Only fill labels if missing (first non-null wins).
    if (!r.label_pt && e.relation_label_pt) r.label_pt = e.relation_label_pt;
    if (!r.label_en && e.relation_label_en) r.label_en = e.relation_label_en;
  }

  for (const r of relations.values()) {
    const subj = geoRef(r.relation);
    const preds = [];
    if (r.label_pt) preds.push(`rdfs:label ${lit(r.label_pt, "pt")}`);
    if (r.label_en) preds.push(`rdfs:label ${lit(r.label_en, "en")}`);

    const domains = [...r.domains];
    const ranges = [...r.ranges];
    if (domains.length === 1) {
      preds.push(`rdfs:domain ${geoRef(domains[0])}`);
    } else if (domains.length > 1) {
      preds.push(`rdfs:domain [ a owl:Class ; owl:unionOf ( ${domains.map(geoRef).join(" ")} ) ]`);
    }
    if (ranges.length === 1) {
      preds.push(`rdfs:range ${geoRef(ranges[0])}`);
    } else if (ranges.length > 1) {
      preds.push(`rdfs:range [ a owl:Class ; owl:unionOf ( ${ranges.map(geoRef).join(" ")} ) ]`);
    }

    const head = `${subj} a owl:ObjectProperty`;
    if (preds.length === 0) {
      out.push(`${head} .`);
    } else {
      out.push(`${head} ;`);
      const body = preds.map((p, i) => `${p}${i === preds.length - 1 ? " ." : " ;"}`).join("\n");
      out.push(indent(body, 4));
    }
    out.push("");
  }

  // ---- Edge triples ----
  out.push("#");
  out.push("# Edges (instance-level relation triples)");
  out.push("#");
  out.push("");

  for (const e of edges) {
    if (!e || !e.source || !e.relation || !e.target) continue;
    out.push(`${geoRef(e.source)} ${geoRef(e.relation)} ${geoRef(e.target)} .`);
  }
  out.push("");

  // ---- Layer1 ↔ Layer1b equivalences (GeoCore ↔ GeoSciML+CGI) ----
  const equiv = loadLayer1Layer1bEquivalence();
  if (equiv && Array.isArray(equiv.mappings) && equiv.mappings.length > 0) {
    out.push("#");
    out.push("# Layer1 (GeoCore) ↔ Layer1b (GeoSciML + CGI Simple Lithology) equivalences");
    out.push(`# Source: data/layer1-layer1b-equivalence.json — ${equiv.meta?.description || ""}`);
    out.push(`# Generated: ${equiv.meta?.generated || ""}`);
    out.push("#");
    out.push("");
    for (const m of equiv.mappings) {
      if (!m.geocore_uri || !m.geosciml_uri || !m.mapping_type) continue;
      out.push(`${uriRef(m.geocore_uri)} ${m.mapping_type} ${uriRef(m.geosciml_uri)} .`);
    }
    out.push("");
  }

  return out.join("\n");
}

// Convenience: load OSDU_CANONICAL and SWEET alignment (if available) and build TTL.
export async function buildTtlAsync(graph) {
  const [canonical, sweetAlignment] = await Promise.all([
    loadOsduCanonical(),
    loadSweetAlignment(),
  ]);
  return buildTtl(graph, { osduCanonical: canonical, sweetAlignment });
}

export default buildTtl;
