/* GSO (Loop3D Geoscience Ontology) extractor — proof of concept
 * Source: https://github.com/Loop3D/GKM (CC BY 4.0, Brodaric & Richard 2021, GSC OF 8796)
 *
 * Reads GSO Turtle modules and emits canonical card entries matching the
 * project's existing schema (cf. scripts/osdu-canonical.js). No rdflib dep —
 * minimal regex-based Turtle parser sufficient for GSO's flat, well-formatted TTL.
 *
 * Usage (CLI):  node scripts/gso-extract.js [path-or-url] > data/gso-faults.json
 * Usage (API):  import { extractGSO } from './gso-extract.js';
 *               await extractGSO();  // writes all modules to data/gso-*.json
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.resolve(__dirname, "..", "data");

const DEFAULT_SRC =
  "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Fault.ttl";

/* All GSO modules to extract when called as a pipeline step */
const GSO_MODULES = [
  {
    src: "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Fault.ttl",
    out: "gso-faults.json",
  },
  {
    src: "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Contact.ttl",
    out: "gso-contacts.json",
  },
  {
    src: "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Fold.ttl",
    out: "gso-folds.json",
  },
  {
    src: "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Foliation.ttl",
    out: "gso-foliations.json",
  },
  {
    src: "https://raw.githubusercontent.com/Loop3D/GKM/master/Loop3D-GSO/Modules/GSO-Geologic_Structure_Lineation.ttl",
    out: "gso-lineations.json",
  },
];

function parsePrefixes(ttl) {
  const map = {};
  for (const m of ttl.matchAll(/@prefix\s+(\w+):\s*<([^>]+)>\s*\./g)) {
    map[m[1]] = m[2];
  }
  return map;
}

async function loadTtl(src) {
  if (/^https?:\/\//.test(src)) {
    const r = await fetch(src);
    if (!r.ok) throw new Error(`HTTP ${r.status} for ${src}`);
    return r.text();
  }
  return fs.readFileSync(path.resolve(src), "utf8");
}

function expand(curie, prefixes) {
  const [p, l] = curie.split(":");
  return prefixes[p] ? prefixes[p] + l : curie;
}

// Extract subject blocks: a subject is anything starting at column 0 and ending with " .\n"
function splitBlocks(ttl) {
  const lines = ttl.split("\n");
  const blocks = [];
  let cur = [];
  let inBlock = false;
  for (const line of lines) {
    if (line.startsWith("#") || line.startsWith("@prefix") || line.startsWith("@base")) continue;
    if (!inBlock && /^\S/.test(line)) {
      inBlock = true;
      cur = [line];
    } else if (inBlock) {
      cur.push(line);
      if (line.trim() === ".") {
        blocks.push(cur.join("\n"));
        cur = [];
        inBlock = false;
      }
    }
  }
  return blocks;
}

function parseBlock(block, prefixes) {
  const head = block.match(/^(\S+)/);
  if (!head) return null;
  const subject = head[1];

  if (!/(?:rdf:type|\ba)\s+owl:Class/.test(block)) return null;

  const labels = {};
  for (const m of block.matchAll(/rdfs:label\s+"([^"]+)"(?:@(\w+))?/g)) {
    const lang = m[2] || "und";
    if (!labels[lang]) labels[lang] = m[1];
  }
  const comments = {};
  for (const m of block.matchAll(/rdfs:comment\s+"([^"]+)"(?:@(\w+))?/g)) {
    const lang = m[2] || "und";
    if (!comments[lang]) comments[lang] = m[1];
  }
  const sources = [
    ...new Set(Array.from(block.matchAll(/dct:source\s+"([^"]+)"(?:@\w+)?/g)).map((m) => m[1])),
  ];
  const parents = Array.from(block.matchAll(/rdfs:subClassOf\s+(\S+?)\s*[;\.\[]/g))
    .map((m) => m[1])
    .filter((x) => /^[a-z]+:[A-Za-z_]/.test(x));

  return {
    curie: subject,
    owl_uri: expand(subject, prefixes),
    pref_label_en: labels.en || labels.und || null,
    pref_label_fr: labels.fr || null,
    definition_en: comments.en || comments.und || null,
    parents,
    sources,
  };
}

function toCard(parsed) {
  const localName = parsed.curie.split(":")[1];
  return [
    `gso:${localName}`,
    {
      owl_uri: parsed.owl_uri,
      gso_class: localName,
      pref_label_en: parsed.pref_label_en,
      pref_label_fr: parsed.pref_label_fr,
      definition_en_canonical: parsed.definition_en,
      parents: parsed.parents,
      sources: parsed.sources,
      attribution: "GSO v1.0 (Brodaric & Richard 2021), GSC OF 8796, CC BY 4.0, DOI 10.4095/328296",
    },
  ];
}

/**
 * Parse a single TTL source and return the structured JSON object.
 * @param {string} src - URL or local file path to a GSO Turtle module
 * @returns {Promise<Object>} - The parsed GSO data object
 */
async function parseGsoModule(src) {
  const ttl = await loadTtl(src);
  const prefixes = parsePrefixes(ttl);
  const blocks = splitBlocks(ttl);
  const classes = blocks.map((b) => parseBlock(b, prefixes)).filter(Boolean);

  const baseMatch = ttl.match(/^#\s*baseURI:\s*(\S+)/m);
  const baseURI = baseMatch ? baseMatch[1] : null;

  return {
    meta: {
      generated: new Date().toISOString(),
      source: src,
      module: path.basename(src).replace(/\.ttl$/, ""),
      base_uri: baseURI,
      prefixes,
      license: "CC BY 4.0",
      attribution: "Brodaric & Richard 2021, GSC Open File 8796, DOI 10.4095/328296",
      class_count: classes.length,
    },
    classes: Object.fromEntries(classes.map(toCard)),
  };
}

/**
 * Extract all GSO modules and write them to data/gso-*.json.
 * Exported for use by generate.js pipeline.
 *
 * @param {Array<{src: string, out: string}>} [modules] - Override module list (defaults to GSO_MODULES)
 * @returns {Promise<{written: string[], errors: string[]}>} - Summary of written files and errors
 */
export async function extractGSO(modules = GSO_MODULES) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const written = [];
  const errors = [];

  for (const { src, out } of modules) {
    const outPath = path.join(DATA_DIR, out);
    try {
      const data = await parseGsoModule(src);
      fs.writeFileSync(outPath, JSON.stringify(data, null, 2) + "\n", "utf8");
      written.push(out);
      console.log(`  [gso-extract] ✓ ${out} (${data.meta.class_count} classes)`);
    } catch (err) {
      errors.push(`${out}: ${err.message}`);
      console.warn(`  [gso-extract] ✗ ${out}: ${err.message}`);
    }
  }

  return { written, errors };
}

/* ── CLI entry point ──────────────────────────────────────────────────────── */
if (import.meta.url === `file://${process.argv[1]}`) {
  const src = process.argv[2];
  if (src) {
    // Single-module mode: parse and print to stdout (original behaviour)
    parseGsoModule(src)
      .then((out) => process.stdout.write(JSON.stringify(out, null, 2) + "\n"))
      .catch((e) => { console.error(e); process.exit(1); });
  } else {
    // No args: extract all modules to data/
    extractGSO()
      .then(({ written, errors }) => {
        console.log(`\nDone. Written: ${written.length}, Errors: ${errors.length}`);
        if (errors.length) process.exit(1);
      })
      .catch((e) => { console.error(e); process.exit(1); });
  }
}
