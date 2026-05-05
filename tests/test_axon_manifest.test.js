/**
 * tests/test_axon_manifest.test.js — Testes para `loadAxonManifest()`
 * (scripts/axon-manifest-loader.js, F9).
 *
 * Cobre:
 *   1. Manifest válido — carrega exploracao com counts esperados.
 *   2. Manifest ausente — retorna [] (fallback gracioso).
 *   3. JSON malformado — lança erro.
 *   4. Arquivo de área inexistente em entry "ingested" — lança erro.
 *   5. Stats drift entre manifest e arquivo — emite warning.
 *   6. IDs duplicados dentro de uma área — emite warning.
 *   7. Área não-`exploracao` sem prefixo `axon-<id>-` — emite warning.
 *
 * Usa fixtures temporárias em /tmp/test-axon-<pid>/ para não tocar nos
 * arquivos reais. Limpeza no teardown.
 *
 * Run: node --test tests/test_axon_manifest.test.js
 */

import { test, describe, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

import { loadAxonManifest } from "../scripts/axon-manifest-loader.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");

/* Diretório de fixtures isolado por PID — evita colisão entre runs em paralelo. */
const TMP_ROOT = path.join(os.tmpdir(), `test-axon-${process.pid}`);

/* ───────────────────────── Helpers ───────────────────────── */

/**
 * Cria um diretório temporário único por teste sob TMP_ROOT.
 * Garante que cada caso tenha sua própria sandbox.
 */
function mkSandbox(name) {
  const dir = path.join(TMP_ROOT, name);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

/**
 * Captura console.warn em um array para assertion sobre warnings emitidos.
 * Retorna `restore()` para devolver o console original.
 */
function captureWarnings() {
  const captured = [];
  const original = console.warn;
  console.warn = (...args) => {
    captured.push(args.map((a) => (typeof a === "string" ? a : JSON.stringify(a))).join(" "));
  };
  return {
    captured,
    restore: () => {
      console.warn = original;
    },
  };
}

/* ─────────────────────── Setup/Teardown ─────────────────────── */

before(() => {
  fs.mkdirSync(TMP_ROOT, { recursive: true });
});

after(() => {
  /* Cleanup recursivo do diretório de fixtures. */
  if (fs.existsSync(TMP_ROOT)) {
    fs.rmSync(TMP_ROOT, { recursive: true, force: true });
  }
});

/* ───────────────────────────────────────────────────────────────
 * 1. Valid manifest loads correctly (live data, default path).
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — valid live manifest", () => {
  test("returns one ingested glossary (exploracao)", () => {
    const result = loadAxonManifest();
    assert.equal(Array.isArray(result), true, "should return an array");
    assert.equal(result.length, 1, "exactly one ingested area expected");
    assert.equal(result[0].areaId, "exploracao");
    assert.ok(result[0].glossary, "glossary object must be present");
  });

  test("glossary structure matches expected counts (1+9+10+2+18)", () => {
    const [{ glossary }] = loadAxonManifest();
    assert.equal((glossary.areas || []).length, 1, "1 area");
    assert.equal((glossary.domains || []).length, 9, "9 domains");
    assert.equal((glossary.subjects || []).length, 10, "10 subjects");
    assert.equal((glossary.subsubjects || []).length, 2, "2 subsubjects");
    assert.equal((glossary.terms || []).length, 18, "18 terms");
  });
});

/* ───────────────────────────────────────────────────────────────
 * 2. Missing manifest returns [].
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — missing manifest", () => {
  test("returns [] when manifestPath does not exist (graceful fallback)", () => {
    const ghostPath = path.join(TMP_ROOT, "non-existent-manifest.json");
    /* Garante ausência. */
    if (fs.existsSync(ghostPath)) fs.unlinkSync(ghostPath);
    const result = loadAxonManifest(ghostPath);
    assert.deepEqual(result, []);
  });
});

/* ───────────────────────────────────────────────────────────────
 * 3. Malformed JSON throws.
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — malformed JSON", () => {
  test("throws Error with descriptive message on invalid JSON", () => {
    const dir = mkSandbox("malformed");
    const badPath = path.join(dir, "bad-manifest.json");
    fs.writeFileSync(badPath, "{invalid json", "utf8");
    assert.throws(
      () => loadAxonManifest(badPath),
      (err) => {
        assert.match(err.message, /could not be parsed/);
        return true;
      }
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 4. Missing ingested area file aborts.
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — missing area file", () => {
  test("throws Error referencing the area id and file path", () => {
    const dir = mkSandbox("missing-area");
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [
          {
            id: "exploracao",
            file: "data/axon/does-not-exist.json",
            status: "ingested",
          },
        ],
      }),
      "utf8"
    );
    assert.throws(
      () => loadAxonManifest(manifestPath, REPO_ROOT),
      (err) => {
        assert.match(err.message, /exploracao/);
        assert.match(err.message, /does-not-exist\.json/);
        return true;
      }
    );
  });

  test("throws when ingested entry is missing id or file fields", () => {
    const dir = mkSandbox("missing-id");
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [{ status: "ingested" /* no id, no file */ }],
      }),
      "utf8"
    );
    assert.throws(() => loadAxonManifest(manifestPath, REPO_ROOT), /missing id or file/);
  });
});

/* ───────────────────────────────────────────────────────────────
 * 5. Stats drift warning.
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — stats drift", () => {
  test("warns when manifest.stats.terms diverge from actual file content", () => {
    const dir = mkSandbox("stats-drift");
    /* Área file sob dir/data/axon/exploracao.json para que o resolver
       relativo encontre. Usa rootDir = dir. */
    const areaDir = path.join(dir, "data", "axon");
    fs.mkdirSync(areaDir, { recursive: true });
    fs.writeFileSync(
      path.join(areaDir, "exploracao.json"),
      JSON.stringify({
        areas: [{ id: "axon-exploracao-area", name_pt: "Exp", axon_type: "Area" }],
        domains: [],
        subjects: [],
        subsubjects: [],
        terms: Array.from({ length: 18 }, (_, i) => ({
          id: `axon-exploracao-term-${i}`,
          name_pt: `t${i}`,
          axon_type: "Termo",
        })),
      }),
      "utf8"
    );
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [
          {
            id: "exploracao",
            file: "data/axon/exploracao.json",
            status: "ingested",
            stats: { areas: 1, domains: 0, subjects: 0, subsubjects: 0, terms: 999 },
          },
        ],
      }),
      "utf8"
    );

    const cap = captureWarnings();
    try {
      const result = loadAxonManifest(manifestPath, dir);
      assert.equal(result.length, 1);
    } finally {
      cap.restore();
    }
    assert.ok(
      cap.captured.some((w) => /stats drift/.test(w) && /terms=999/.test(w)),
      `expected 'stats drift' warning mentioning terms=999. captured: ${cap.captured.join(" | ")}`
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 6. Duplicate ID warning.
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — duplicate IDs", () => {
  test("warns on two entities with the same id within an area", () => {
    const dir = mkSandbox("dup-ids");
    const areaDir = path.join(dir, "data", "axon");
    fs.mkdirSync(areaDir, { recursive: true });
    fs.writeFileSync(
      path.join(areaDir, "exploracao.json"),
      JSON.stringify({
        areas: [{ id: "axon-dup-area", name_pt: "X", axon_type: "Area" }],
        domains: [
          { id: "axon-dup-X", name_pt: "first", axon_type: "Domínio" },
          /* Mesma id em terms — viola unicidade global do area file. */
        ],
        subjects: [],
        subsubjects: [],
        terms: [{ id: "axon-dup-X", name_pt: "second", axon_type: "Termo" }],
      }),
      "utf8"
    );
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [{ id: "exploracao", file: "data/axon/exploracao.json", status: "ingested" }],
      }),
      "utf8"
    );

    const cap = captureWarnings();
    try {
      loadAxonManifest(manifestPath, dir);
    } finally {
      cap.restore();
    }
    assert.ok(
      cap.captured.some((w) => /duplicate entity ID/.test(w) && /axon-dup-X/.test(w)),
      `expected 'duplicate entity ID' warning. captured: ${cap.captured.join(" | ")}`
    );
  });
});

/* ───────────────────────────────────────────────────────────────
 * 7. Non-`exploracao` area without `axon-<id>-` prefix warning.
 * ─────────────────────────────────────────────────────────────── */

describe("loadAxonManifest — area-id prefix discipline", () => {
  test("warns when non-exploracao area has IDs without 'axon-<area_id>-' prefix", () => {
    const dir = mkSandbox("prefix-violation");
    const areaDir = path.join(dir, "data", "axon");
    fs.mkdirSync(areaDir, { recursive: true });
    /* IDs SEM `axon-producao-` prefix devem disparar o warning. */
    fs.writeFileSync(
      path.join(areaDir, "producao.json"),
      JSON.stringify({
        areas: [{ id: "wrong-prefix-area", name_pt: "Produção", axon_type: "Area" }],
        domains: [
          { id: "another-bad-id", name_pt: "Op Poço", axon_type: "Domínio" },
          { id: "axon-producao-dom-correct", name_pt: "OK", axon_type: "Domínio" },
        ],
        subjects: [],
        subsubjects: [],
        terms: [],
      }),
      "utf8"
    );
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [{ id: "producao", file: "data/axon/producao.json", status: "ingested" }],
      }),
      "utf8"
    );

    const cap = captureWarnings();
    try {
      loadAxonManifest(manifestPath, dir);
    } finally {
      cap.restore();
    }
    assert.ok(
      cap.captured.some(
        (w) => /do not start with "axon-producao-"/.test(w) || /axon-producao-/.test(w)
      ),
      `expected prefix warning for area 'producao'. captured: ${cap.captured.join(" | ")}`
    );
    /* Confirma que pelo menos um dos offenders é mencionado. */
    assert.ok(
      cap.captured.some((w) => /wrong-prefix-area|another-bad-id/.test(w)),
      `expected one of the bad ids to be listed. captured: ${cap.captured.join(" | ")}`
    );
  });

  test("does not warn for exploracao even with non-prefixed IDs (whitelisted)", () => {
    const dir = mkSandbox("exploracao-no-prefix-check");
    const areaDir = path.join(dir, "data", "axon");
    fs.mkdirSync(areaDir, { recursive: true });
    /* IDs históricos do exploracao podem usar `axon-domain-*`, `axon-term-*`,
       etc.; não devem disparar warning. */
    fs.writeFileSync(
      path.join(areaDir, "exploracao.json"),
      JSON.stringify({
        areas: [{ id: "axon-domain-area-exploracao", name_pt: "Exp", axon_type: "Area" }],
        domains: [{ id: "axon-domain-geomecanica", name_pt: "Geomec", axon_type: "Domínio" }],
        subjects: [],
        subsubjects: [],
        terms: [{ id: "axon-term-furo", name_pt: "Furo", axon_type: "Termo" }],
      }),
      "utf8"
    );
    const manifestPath = path.join(dir, "manifest.json");
    fs.writeFileSync(
      manifestPath,
      JSON.stringify({
        areas: [{ id: "exploracao", file: "data/axon/exploracao.json", status: "ingested" }],
      }),
      "utf8"
    );

    const cap = captureWarnings();
    try {
      loadAxonManifest(manifestPath, dir);
    } finally {
      cap.restore();
    }
    /* Não deve haver warning de prefix discipline para exploracao. */
    assert.ok(
      !cap.captured.some((w) => /do not start with/.test(w)),
      `should NOT emit prefix warning for 'exploracao'. captured: ${cap.captured.join(" | ")}`
    );
  });
});
