#!/usr/bin/env node
/**
 * validate-shacl.js — Node.js thin wrapper for SHACL validation.
 *
 * If rdf-validate-shacl is installed, validates data/geolytics.ttl against
 * data/geolytics-shapes.ttl using that library.
 *
 * If rdf-validate-shacl is NOT installed, prints a helpful message and
 * delegates to the Python implementation.
 *
 * Usage:
 *   node scripts/validate-shacl.js
 *   node scripts/validate-shacl.js --data data/geolytics.ttl
 *   node scripts/validate-shacl.js --shapes data/geolytics-shapes.ttl
 */

import { createRequire } from "node:module";
import { execSync, spawnSync } from "node:child_process";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

// Parse CLI arguments
const args = process.argv.slice(2);
function getArg(flag) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

const dataPath = getArg("--data") || path.join(ROOT, "data", "geolytics.ttl");
const shapesPath = getArg("--shapes") || path.join(ROOT, "data", "geolytics-shapes.ttl");
const vocabPath = getArg("--ontology") || path.join(ROOT, "data", "geolytics-vocab.ttl");

// Check files exist
for (const [label, p] of [
  ["Dados", dataPath],
  ["Shapes", shapesPath],
]) {
  if (!fs.existsSync(p)) {
    console.error(`[ERRO] ${label}: arquivo nao encontrado: ${p}`);
    process.exit(2);
  }
}

// Try to load rdf-validate-shacl
let shaclLib = null;
try {
  const require = createRequire(import.meta.url);
  shaclLib = require("rdf-validate-shacl");
} catch {
  // Not installed — fall through to Python delegate
}

if (shaclLib) {
  await runWithNodeLib(shaclLib, dataPath, shapesPath, vocabPath);
} else {
  runWithPythonDelegate(dataPath, shapesPath, vocabPath);
}

// ─────────────────────────────────────────────────────────────────────────────
// Node.js validation using rdf-validate-shacl
// ─────────────────────────────────────────────────────────────────────────────

async function runWithNodeLib(SHACLValidator, dataFile, shapesFile, vocabFile) {
  let rdflib;
  try {
    const require = createRequire(import.meta.url);
    rdflib = require("@rdfjs/dataset");
  } catch {
    console.error(
      "[AVISO] rdf-validate-shacl esta instalado, mas @rdfjs/dataset nao foi encontrado.\n" +
        "Execute: npm install @rdfjs/dataset n3\n" +
        "Ou use o validador Python: python scripts/validate-shacl.py"
    );
    process.exit(1);
  }

  // Use N3 parser (Turtle)
  let N3;
  try {
    const require = createRequire(import.meta.url);
    N3 = require("n3");
  } catch {
    console.error(
      "[AVISO] Modulo n3 nao encontrado. Execute: npm install n3\n" +
        "Ou use: python scripts/validate-shacl.py"
    );
    process.exit(1);
  }

  console.log("=".repeat(70));
  console.log("Validador SHACL — GeoBrain (Node.js / rdf-validate-shacl)");
  console.log("=".repeat(70));
  console.log(`  Dados   : ${dataFile}`);
  console.log(`  Shapes  : ${shapesFile}`);

  async function parseTurtle(filePath) {
    const parser = new N3.Parser({ format: "Turtle" });
    const store = new N3.Store();
    const content = fs.readFileSync(filePath, "utf8");
    return new Promise((resolve, reject) => {
      parser.parse(content, (err, quad) => {
        if (err) return reject(err);
        if (quad) store.addQuad(quad);
        else resolve(store);
      });
    });
  }

  let dataStore, shapesStore;
  try {
    dataStore = await parseTurtle(dataFile);
    shapesStore = await parseTurtle(shapesFile);
  } catch (err) {
    console.error(`[ERRO] Falha ao parsear Turtle: ${err.message}`);
    process.exit(2);
  }

  const validator = new SHACLValidator(shapesStore, { factory: N3.DataFactory });
  const report = await validator.validate(dataStore);

  console.log();
  console.log("─".repeat(70));
  if (report.conforms) {
    console.log("RESULTADO: CONFORME");
    console.log("O grafo de dados esta em conformidade com todos os shapes SHACL.");
  } else {
    const n = report.results.length;
    console.log(`RESULTADO: NAO CONFORME — ${n} violacao(oes) encontrada(s)`);
    console.log();
    for (let i = 0; i < report.results.length; i++) {
      const r = report.results[i];
      console.log(`  [${i + 1}] Violacao`);
      if (r.focusNode) console.log(`       No          : ${r.focusNode.value}`);
      if (r.path) console.log(`       Propriedade : ${r.path.value}`);
      if (r.message[0]) console.log(`       Mensagem    : ${r.message[0].value}`);
      console.log();
    }
  }
  console.log("─".repeat(70));

  process.exit(report.conforms ? 0 : 1);
}

// ─────────────────────────────────────────────────────────────────────────────
// Python delegate when rdf-validate-shacl is not available
// ─────────────────────────────────────────────────────────────────────────────

function runWithPythonDelegate(dataFile, shapesFile, vocabFile) {
  console.log("");
  console.log("rdf-validate-shacl nao esta instalado.");
  console.log("");
  console.log("Opcoes para instalar (escolha uma):");
  console.log("  npm install rdf-validate-shacl n3");
  console.log("");
  console.log("Delegando para o validador Python (recomendado):");
  console.log("  python3 -m pip install --user pyshacl rdflib");
  console.log("  python scripts/validate-shacl.py");
  console.log("");

  // Try to run Python automatically
  const pythonScript = path.join(__dirname, "validate-shacl.py");
  if (!fs.existsSync(pythonScript)) {
    console.error("[ERRO] scripts/validate-shacl.py nao encontrado.");
    process.exit(2);
  }

  // Try python3 first, then python
  for (const cmd of ["python3", "python"]) {
    const result = spawnSync(cmd, ["--version"], { encoding: "utf8" });
    if (result.status === 0) {
      console.log(`Executando: ${cmd} scripts/validate-shacl.py`);
      console.log("");
      const run = spawnSync(
        cmd,
        [pythonScript, "--data", dataFile, "--shapes", shapesFile, "--ontology", vocabFile],
        { stdio: "inherit", encoding: "utf8" }
      );
      process.exit(run.status ?? 1);
    }
  }

  console.error("[ERRO] Python nao encontrado. Instale Python 3.8+ e execute:");
  console.error("  python scripts/validate-shacl.py");
  process.exit(2);
}
