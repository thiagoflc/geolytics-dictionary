"use strict";
/**
 * validate-entity-graph.js — CI lint for data/entity-graph.json
 *
 * Detects:
 *   1. Orphan nodes      — nodes with no incoming or outgoing edges
 *   2. Broken cross-links — edges referencing non-existent node IDs
 *   3. Invalid layers    — geocoverage values not in known layer IDs
 *   4. Missing fields    — nodes without id, label, or type
 *   5. Duplicate IDs     — nodes whose id appears more than once
 *   6. Bad GeoSciML URIs — geosciml_uri not starting with http://geosciml.org/
 *
 * Usage:
 *   node scripts/validate-entity-graph.js
 *   node scripts/validate-entity-graph.js --fix   (removes duplicate nodes)
 *
 * Exit codes:
 *   0 — all checks pass (or only warnings)
 *   1 — one or more errors found
 */

const fs = require("node:fs");
const path = require("node:path");

// ---------------------------------------------------------------------------
// ANSI colour helpers
// ---------------------------------------------------------------------------
const GREEN = "\x1b[32m";
const RED = "\x1b[31m";
const YELLOW = "\x1b[33m";
const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";

const ok = (msg) => `${GREEN}✓${RESET} ${msg}`;
const err = (msg) => `${RED}✗${RESET} ${msg}`;
const warn = (msg) => `${YELLOW}⚠${RESET} ${msg}`;

// ---------------------------------------------------------------------------
// File loading
// ---------------------------------------------------------------------------
const ROOT = path.resolve(__dirname, "..");

function loadJson(relPath) {
  const absPath = path.join(ROOT, relPath);
  if (!fs.existsSync(absPath)) {
    console.error(err(`File not found: ${relPath}`));
    process.exit(1);
  }
  try {
    return JSON.parse(fs.readFileSync(absPath, "utf8"));
  } catch (e) {
    console.error(err(`Failed to parse ${relPath}: ${e.message}`));
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Build valid layer set from ai/ontology-map.json
// ---------------------------------------------------------------------------
function buildValidLayers(ontologyMap) {
  const layers = ontologyMap.layers || {};
  const ids = new Set();
  for (const entry of Object.values(layers)) {
    if (entry && entry.id) ids.add(entry.id);
  }
  return ids;
}

// ---------------------------------------------------------------------------
// Check functions
// ---------------------------------------------------------------------------

/** 1. Orphan nodes — nodes with no incoming or outgoing edges */
function checkOrphanNodes(nodes, edges) {
  const connected = new Set([...edges.map((e) => e.source), ...edges.map((e) => e.target)]);
  return nodes.filter((n) => !connected.has(n.id));
}

/** 2. Broken cross-links — edges referencing non-existent node IDs */
function checkBrokenEdges(nodes, edges) {
  const nodeIds = new Set(nodes.map((n) => n.id));
  return edges.filter((e) => !nodeIds.has(e.source) || !nodeIds.has(e.target));
}

/** 3. Invalid layers — geocoverage values not in known layer IDs */
function checkInvalidLayers(nodes, validLayers) {
  const errors = [];
  for (const node of nodes) {
    const invalid = (node.geocoverage || []).filter((l) => !validLayers.has(l));
    if (invalid.length) {
      errors.push({ node: node.id, invalid_layers: invalid });
    }
  }
  return errors;
}

/** 4. Missing required fields — nodes without id, label, or type */
function checkMissingFields(nodes) {
  return nodes.filter((n) => !n.id || !n.label || !n.type);
}

/** 5. Duplicate IDs */
function checkDuplicateIds(nodes) {
  const seen = new Set();
  return nodes.filter((n) => {
    const dup = seen.has(n.id);
    seen.add(n.id);
    return dup;
  });
}

/** 6. GeoSciML URI format — must start with http://geosciml.org/ if present */
function checkGeoscimlUris(nodes) {
  return nodes.filter((n) => n.geosciml_uri && !n.geosciml_uri.startsWith("http://geosciml.org/"));
}

// ---------------------------------------------------------------------------
// --fix helpers
// ---------------------------------------------------------------------------

/**
 * Remove duplicate nodes (keep first occurrence).
 * Returns the deduplicated node array.
 */
function fixDuplicates(nodes) {
  const seen = new Set();
  return nodes.filter((n) => {
    if (seen.has(n.id)) return false;
    seen.add(n.id);
    return true;
  });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const fix = process.argv.includes("--fix");

  console.log(`\n${BOLD}Entity-graph validation${RESET}`);
  console.log("─".repeat(50));

  // Load data
  const graph = loadJson("data/entity-graph.json");
  const ontologyMap = loadJson("ai/ontology-map.json");

  let nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const validLayers = buildValidLayers(ontologyMap);

  console.log(`  Graph version : ${graph.version || "(unset)"}`);
  console.log(`  Nodes         : ${nodes.length}`);
  console.log(`  Edges         : ${edges.length}`);
  console.log(`  Valid layers  : ${[...validLayers].sort().join(", ")}`);
  console.log("");

  let hasErrors = false;
  let totalErrors = 0;
  let totalWarns = 0;

  // ── 1. Orphan nodes ──────────────────────────────────────────────────────
  const orphans = checkOrphanNodes(nodes, edges);
  if (orphans.length === 0) {
    console.log(ok(`Orphan nodes       : none`));
  } else {
    // Orphans are a warning — isolated nodes may be intentional stubs
    totalWarns += orphans.length;
    console.log(warn(`Orphan nodes       : ${orphans.length} node(s) have no edges`));
    for (const n of orphans) {
      console.log(`   ${YELLOW}→${RESET} ${n.id} (${n.label || "(no label)"})`);
    }
  }

  // ── 2. Broken edges ──────────────────────────────────────────────────────
  const broken = checkBrokenEdges(nodes, edges);
  if (broken.length === 0) {
    console.log(ok(`Broken edges       : none`));
  } else {
    hasErrors = true;
    totalErrors += broken.length;
    console.log(err(`Broken edges       : ${broken.length} edge(s) reference missing nodes`));
    for (const e of broken) {
      const srcOk = new Set(nodes.map((n) => n.id)).has(e.source)
        ? ""
        : ` ${RED}(missing source)${RESET}`;
      const tgtOk = new Set(nodes.map((n) => n.id)).has(e.target)
        ? ""
        : ` ${RED}(missing target)${RESET}`;
      console.log(
        `   ${RED}→${RESET} ${e.source}${srcOk} → ${e.target}${tgtOk} [${e.relation || "?"}]`
      );
    }
  }

  // ── 3. Invalid layers ────────────────────────────────────────────────────
  const badLayers = checkInvalidLayers(nodes, validLayers);
  if (badLayers.length === 0) {
    console.log(ok(`Invalid layers     : none`));
  } else {
    hasErrors = true;
    totalErrors += badLayers.length;
    console.log(
      err(`Invalid layers     : ${badLayers.length} node(s) reference unknown layer IDs`)
    );
    for (const b of badLayers) {
      console.log(`   ${RED}→${RESET} ${b.node}: [${b.invalid_layers.join(", ")}]`);
    }
  }

  // ── 4. Missing required fields ───────────────────────────────────────────
  const missing = checkMissingFields(nodes);
  if (missing.length === 0) {
    console.log(ok(`Missing fields     : none`));
  } else {
    hasErrors = true;
    totalErrors += missing.length;
    console.log(err(`Missing fields     : ${missing.length} node(s) lack id, label, or type`));
    for (const n of missing) {
      const missing_fields = [];
      if (!n.id) missing_fields.push("id");
      if (!n.label) missing_fields.push("label");
      if (!n.type) missing_fields.push("type");
      console.log(
        `   ${RED}→${RESET} ${n.id || "(no id)"}: missing [${missing_fields.join(", ")}]`
      );
    }
  }

  // ── 5. Duplicate IDs ─────────────────────────────────────────────────────
  const dupes = checkDuplicateIds(nodes);
  if (dupes.length === 0) {
    console.log(ok(`Duplicate IDs      : none`));
  } else {
    // --fix: auto-remove duplicate nodes
    if (fix) {
      nodes = fixDuplicates(nodes);
      graph.nodes = nodes;
      fs.writeFileSync(
        path.join(ROOT, "data/entity-graph.json"),
        JSON.stringify(graph, null, 2) + "\n",
        "utf8"
      );
      totalWarns += dupes.length;
      console.log(
        warn(`Duplicate IDs      : ${dupes.length} duplicate(s) auto-removed (--fix applied)`)
      );
    } else {
      hasErrors = true;
      totalErrors += dupes.length;
      console.log(err(`Duplicate IDs      : ${dupes.length} duplicate node ID(s) found`));
      for (const n of dupes) {
        console.log(`   ${RED}→${RESET} ${n.id}`);
      }
      console.log(`   ${YELLOW}Tip: run with --fix to auto-remove duplicates${RESET}`);
    }
  }

  // ── 6. GeoSciML URI format ───────────────────────────────────────────────
  const badUris = checkGeoscimlUris(nodes);
  if (badUris.length === 0) {
    console.log(ok(`GeoSciML URIs      : all valid (or absent)`));
  } else {
    hasErrors = true;
    totalErrors += badUris.length;
    console.log(err(`GeoSciML URIs      : ${badUris.length} node(s) have malformed geosciml_uri`));
    for (const n of badUris) {
      console.log(`   ${RED}→${RESET} ${n.id}: "${n.geosciml_uri}"`);
    }
    console.log(`   ${YELLOW}Expected prefix: http://geosciml.org/${RESET}`);
  }

  // ── Summary ───────────────────────────────────────────────────────────────
  console.log("\n" + "─".repeat(50));
  if (hasErrors) {
    console.log(`${RED}${BOLD}FAILED${RESET}  ${totalErrors} error(s), ${totalWarns} warning(s)`);
    process.exit(1);
  } else if (totalWarns > 0) {
    console.log(`${YELLOW}${BOLD}PASSED with warnings${RESET}  0 errors, ${totalWarns} warning(s)`);
    process.exit(0);
  } else {
    console.log(`${GREEN}${BOLD}PASSED${RESET}  All checks passed.`);
    process.exit(0);
  }
}

main();
