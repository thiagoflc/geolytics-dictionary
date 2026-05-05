/**
 * axon-manifest-loader.js — Loader puro para `data/axon/manifest.json`.
 *
 * Extraído de scripts/generate.js para permitir testes unitários (ver
 * tests/test_axon_manifest.test.js). A lógica é idêntica à versão original
 * inline, mas o caminho do manifest agora é injetável via argumento, mantendo
 * o comportamento default (data/axon/manifest.json relativo ao repo) intacto.
 *
 * Não-breaking: chamar `loadAxonManifest()` sem argumento reproduz o
 * comportamento histórico.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_ROOT = path.resolve(__dirname, "..");
const DEFAULT_MANIFEST_PATH = path.join(DEFAULT_ROOT, "data", "axon", "manifest.json");

/**
 * Lê e valida um manifest Axon Petrobras, retornando um array de
 * `{ areaId, glossary }` para cada area com `status === "ingested"`.
 *
 * Erros fatais (lança Error):
 *   - Manifest existe mas é JSON malformado.
 *   - Entry "ingested" sem `id` ou `file`.
 *   - Entry "ingested" referencia arquivo inexistente.
 *   - Arquivo da área é JSON malformado.
 *
 * Soft warnings (console.warn):
 *   - stats drift entre manifest.stats.* e contagens reais do arquivo.
 *   - IDs duplicados dentro de uma mesma área.
 *   - área diferente de "exploracao" cujos IDs não começam com `axon-{id}-`.
 *
 * Comportamento gracioso: se o manifest não existe, retorna `[]` (preserva
 * o fallback histórico — Axon sub-graph fica vazio).
 *
 * @param {string} [manifestPath] Caminho absoluto para o manifest. Default:
 *   `<repo>/data/axon/manifest.json`.
 * @param {string} [rootDir] Diretório-raiz usado para resolver `entry.file`
 *   relativos. Default: `<repo>` (dois níveis acima do manifest default), ou
 *   o avô do `manifestPath` quando customizado. Caminhos absolutos em
 *   `entry.file` ignoram `rootDir`.
 * @returns {{areaId: string, glossary: object}[]}
 */
export function loadAxonManifest(manifestPath, rootDir) {
  const resolvedManifestPath = manifestPath || DEFAULT_MANIFEST_PATH;
  if (!fs.existsSync(resolvedManifestPath)) {
    /* Sem manifest — preserva comportamento antigo (sub-graph Axon vazio). */
    return [];
  }
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(resolvedManifestPath, "utf8"));
  } catch (e) {
    throw new Error(`Axon manifest could not be parsed: ${e.message}`);
  }
  const ingested = (manifest.areas || []).filter((a) => a.status === "ingested");
  const out = [];
  /* Resolve entry.file relativos ao rootDir. Default: avô do manifest
     (data/axon/manifest.json → <repo>). */
  const resolvedRoot = rootDir || path.resolve(path.dirname(resolvedManifestPath), "..", "..");
  for (const entry of ingested) {
    if (!entry.id || !entry.file) {
      throw new Error(`Axon manifest: ingested area missing id or file (${JSON.stringify(entry)})`);
    }
    const areaPath = path.isAbsolute(entry.file) ? entry.file : path.join(resolvedRoot, entry.file);
    if (!fs.existsSync(areaPath)) {
      throw new Error(
        `Axon manifest references ingested area "${entry.id}" at ${entry.file}, but the file does not exist.`
      );
    }
    let glossary;
    try {
      glossary = JSON.parse(fs.readFileSync(areaPath, "utf8"));
    } catch (e) {
      throw new Error(`Axon area "${entry.id}" (${entry.file}) parse failed: ${e.message}`);
    }
    /* Soft validation 1 — stats drift. */
    const actual = {
      areas: (glossary.areas || []).length,
      domains: (glossary.domains || []).length,
      subjects: (glossary.subjects || []).length,
      subsubjects: (glossary.subsubjects || []).length,
      terms: (glossary.terms || []).length,
    };
    if (entry.stats) {
      for (const k of Object.keys(actual)) {
        const claimed = entry.stats[k];
        if (typeof claimed === "number" && claimed !== actual[k]) {
          console.warn(
            `  [warn] Axon manifest stats drift for area "${entry.id}": stats.${k}=${claimed} but file has ${actual[k]}.`
          );
        }
      }
    }
    /* Soft validation 2 — duplicate IDs within the area file. */
    const idSeen = new Set();
    const allEntries = [
      ...(glossary.areas || []),
      ...(glossary.domains || []),
      ...(glossary.subjects || []),
      ...(glossary.subsubjects || []),
      ...(glossary.terms || []),
    ];
    for (const e of allEntries) {
      if (!e.id) continue;
      if (idSeen.has(e.id)) {
        console.warn(`  [warn] Axon area "${entry.id}": duplicate entity ID "${e.id}".`);
      }
      idSeen.add(e.id);
    }
    /* Soft validation 3 — non-exploracao must use axon-{area_id}- prefix. */
    if (entry.id !== "exploracao") {
      const expectedPrefix = `axon-${entry.id}-`;
      const offenders = allEntries
        .filter((e) => e.id && !e.id.startsWith(expectedPrefix))
        .map((e) => e.id);
      if (offenders.length) {
        console.warn(
          `  [warn] Axon area "${entry.id}": ${offenders.length} entity ID(s) do not start with "${expectedPrefix}". First few: ${offenders
            .slice(0, 3)
            .join(", ")}`
        );
      }
    }
    out.push({ areaId: entry.id, glossary });
  }
  return out;
}
