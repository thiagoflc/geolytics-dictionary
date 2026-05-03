#!/usr/bin/env node
/**
 * build-ontology-doc.js
 *
 * Gera docs/ONTOLOGY.md a partir de:
 *   - data/ontopetro.json    (ontologia formal — 6 modulos)
 *   - data/geomechanics.json (modulo MEM P2.7)
 *   - data/seismic-acquisition.json    (modulo sismico P2.8 — aquisicao)
 *   - data/seismic-processing.json     (modulo sismico P2.8 — processamento)
 *   - data/seismic-inversion-attributes.json (modulo sismico P2.8 — inversao)
 *
 * Uso:
 *   node scripts/build-ontology-doc.js
 *   node scripts/build-ontology-doc.js --out docs/ONTOLOGY.md
 */

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

function load(relPath) {
  const abs = path.join(ROOT, relPath);
  return JSON.parse(fs.readFileSync(abs, "utf8"));
}

function outArg() {
  const idx = process.argv.indexOf("--out");
  if (idx !== -1 && process.argv[idx + 1]) return process.argv[idx + 1];
  return path.join(ROOT, "docs", "ONTOLOGY.md");
}

// ---------------------------------------------------------------------------
// Load sources
// ---------------------------------------------------------------------------

const ontopetro = load("data/ontopetro.json");
const geomech = load("data/geomechanics.json");
const seisAcq = load("data/seismic-acquisition.json");
const seisProc = load("data/seismic-processing.json");
const seisInv = load("data/seismic-inversion-attributes.json");

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function tableHeader(cols) {
  const header = "| " + cols.join(" | ") + " |";
  const sep = "|" + cols.map(() => "---|").join("");
  return header + "\n" + sep;
}

function row(cells) {
  return (
    "| " +
    cells
      .map((c) =>
        String(c ?? "")
          .replace(/\|/g, "\\|")
          .replace(/\n/g, " ")
      )
      .join(" | ") +
    " |"
  );
}

function safeSources(sources) {
  if (!sources) return "";
  if (Array.isArray(sources)) return sources.join(", ");
  return String(sources);
}

function toArray(val) {
  if (!val) return [];
  if (Array.isArray(val)) return val;
  // object keyed by id — convert to array
  return Object.values(val);
}

function classTable(classes) {
  const arr = toArray(classes);
  if (arr.length === 0) return "_Nenhuma classe neste modulo._\n";
  const lines = [
    tableHeader([
      "ID",
      "Nome PT",
      "Nome EN",
      "Superclasse",
      "Dominio",
      "Descricao (resumo)",
      "Fontes",
    ]),
  ];
  for (const c of arr) {
    lines.push(
      row([
        c.id ?? "",
        c.name_pt ?? c.name ?? "",
        c.name_en ?? c.name ?? "",
        c.superclass ?? "",
        c.domain ?? "",
        (c.description ?? "").substring(0, 80) + ((c.description ?? "").length > 80 ? "..." : ""),
        safeSources(c.sources),
      ])
    );
  }
  return lines.join("\n") + "\n";
}

function propertyTable(props) {
  const arr = toArray(props);
  if (arr.length === 0) return "_Nenhuma propriedade neste modulo._\n";
  const lines = [tableHeader(["ID", "Nome", "Tipo", "Dominio", "Range / Unidade", "Obrigatorio"])];
  for (const p of arr) {
    lines.push(
      row([
        p.id ?? "",
        p.name ?? p.label ?? "",
        p.type ?? p.property_type ?? "",
        p.domain ?? "",
        p.range ?? p.unit ?? "",
        p.required ? "sim" : "nao",
      ])
    );
  }
  return lines.join("\n") + "\n";
}

function relationTable(rels) {
  const arr = toArray(rels);
  if (arr.length === 0) return "_Nenhuma relacao neste modulo._\n";
  const lines = [
    tableHeader(["ID", "Nome", "Dominio (classe)", "Range (classe)", "Cardinalidade"]),
  ];
  for (const r of arr) {
    lines.push(
      row([r.id ?? "", r.name ?? r.label ?? "", r.domain ?? "", r.range ?? "", r.cardinality ?? ""])
    );
  }
  return lines.join("\n") + "\n";
}

function instanceTable(insts) {
  const arr = toArray(insts);
  if (arr.length === 0) return "_Nenhuma instancia neste modulo._\n";
  const lines = [tableHeader(["ID", "Nome", "Tipo (classe)", "Descricao"])];
  for (const i of arr) {
    lines.push(
      row([
        i.id ?? "",
        i.name ?? i.label ?? "",
        i.type ?? i.class ?? "",
        (i.description ?? "").substring(0, 80),
      ])
    );
  }
  return lines.join("\n") + "\n";
}

function moduleSection(title, anchor, data, meta) {
  const classes = toArray(data.classes);
  const props = toArray(data.properties);
  const rels = toArray(data.relations);
  const insts = toArray(data.instances);

  let out = `\n## ${title}\n\n`;
  if (meta) out += meta + "\n\n";
  out += `**Totais**: ${classes.length} classes, ${props.length} propriedades, ${rels.length} relacoes, ${insts.length} instancias.\n\n`;

  out += `### Classes\n\n${classTable(classes)}\n`;
  out += `### Propriedades\n\n${propertyTable(props)}\n`;
  out += `### Relacoes\n\n${relationTable(rels)}\n`;
  if (insts.length > 0) {
    out += `### Instancias\n\n${instanceTable(insts)}\n`;
  }
  return out;
}

// ---------------------------------------------------------------------------
// Build document
// ---------------------------------------------------------------------------

const now = new Date().toISOString().split("T")[0];

let doc = `# Referencia de Classes e Propriedades — Ontologia Geolytics

> Gerado automaticamente por \`scripts/build-ontology-doc.js\` em ${now}.
> Nao edite manualmente — execute \`node scripts/build-ontology-doc.js\` para regenerar.

Este documento lista todas as classes, propriedades, relacoes e instancias formais
dos modulos de ontologia do GeoBrain, extraidas diretamente dos arquivos JSON canonicos.

---

## Indice de modulos

| Modulo | Fonte | Classes | Propriedades | Relacoes | Instancias |
|---|---|---|---|---|---|
| Ontopetro (base) | \`data/ontopetro.json\` | ${toArray(ontopetro.classes).length} | ${toArray(ontopetro.properties).length} | ${toArray(ontopetro.relations).length} | ${toArray(ontopetro.instances).length} |
| Geomecanica MEM P2.7 | \`data/geomechanics.json\` | ${toArray(geomech.classes).length} | ${toArray(geomech.properties).length} | ${toArray(geomech.relations).length} | ${toArray(geomech.instances).length} |
| Sismico Aquisicao P2.8 | \`data/seismic-acquisition.json\` | ${toArray(seisAcq.classes).length} | ${toArray(seisAcq.properties).length} | ${toArray(seisAcq.relations).length} | ${toArray(seisAcq.instances).length} |
| Sismico Processamento P2.8 | \`data/seismic-processing.json\` | ${toArray(seisProc.classes).length} | ${toArray(seisProc.properties).length} | ${toArray(seisProc.relations).length} | ${toArray(seisProc.instances).length} |
| Sismico Inversao e Atributos P2.8 | \`data/seismic-inversion-attributes.json\` | ${toArray(seisInv.classes).length} | ${toArray(seisInv.properties).length} | ${toArray(seisInv.relations).length} | ${toArray(seisInv.instances).length} |

---
`;

// Ontopetro module — use architecture meta if present
const ontopetroMeta = ontopetro.meta
  ? `Versao: \`${ontopetro.meta.version}\`. Fontes: ${(ontopetro.meta.sources || []).join(", ")}.`
  : "";

doc += moduleSection(
  "Ontopetro — Ontologia Formal de Geociencias de Petroleo",
  "ontopetro",
  ontopetro,
  ontopetroMeta
);

doc += moduleSection(
  "Geomecanica MEM (P2.7)",
  "geomechanics",
  geomech,
  "Modulo de Mecanica de Rochas e Modelo de Terra Mecanico (MEM 1D). " +
    "Ver `docs/GEOMECHANICS.md` para documentacao completa."
);

doc += moduleSection(
  "Sismico — Aquisicao (P2.8)",
  "seismic-acquisition",
  seisAcq,
  "Referencias: Yilmaz (2001), Sheriff & Geldart (1995). " +
    "Ver `docs/SEISMIC.md` para documentacao completa."
);

doc += moduleSection(
  "Sismico — Processamento (P2.8)",
  "seismic-processing",
  seisProc,
  "Referencias: Yilmaz (2001). " + "Ver `docs/SEISMIC.md` para documentacao completa."
);

doc += moduleSection(
  "Sismico — Inversao e Atributos (P2.8)",
  "seismic-inversion",
  seisInv,
  "Referencias: Russell (1988), Connolly (1999), Chopra & Marfurt (2007), Coleou et al. (2003). " +
    "Ver `docs/SEISMIC.md` para documentacao completa."
);

doc += `
---

## Como regenerar

\`\`\`bash
node scripts/build-ontology-doc.js
\`\`\`

Para especificar destino:

\`\`\`bash
node scripts/build-ontology-doc.js --out docs/ONTOLOGY.md
\`\`\`
`;

// ---------------------------------------------------------------------------
// Write output
// ---------------------------------------------------------------------------

const outPath = outArg();
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, doc, "utf8");
console.log(`Escrito: ${outPath} (${doc.length} bytes, ~${doc.split("\n").length} linhas)`);
