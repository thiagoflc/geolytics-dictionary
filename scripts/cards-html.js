/**
 * cards-html.js — Builds a self-contained HTML page (index-cards.html)
 * listing every entity-graph node as a navigable pyLODE-style card.
 *
 * Usage:
 *   import { buildCardsHtml } from './cards-html.js';
 *   const html = buildCardsHtml(graph);   // graph = JSON read from data/entity-graph.json
 *
 * Produces a single HTML string with:
 *   - sticky header (links back to D3 view, TTL, WebVOWL)
 *   - left sticky sidebar TOC grouped by node type
 *   - one <section class="card"> per node with full metadata
 *   - client-side search (no libraries)
 *   - light/dark via prefers-color-scheme, mobile responsive
 */

// ---------- Constants -----------------------------------------------------

const TYPE_COLORS = {
  operational: "#378ADD",
  contractual: "#7F77DD",
  actor: "#D85A30",
  instrument: "#888780",
  geological: "#639922",
  equipment: "#C77B30",
  analytical: "#E67E22",
};

const TYPE_LABELS = {
  operational: "Operacional",
  contractual: "Contratual",
  actor: "Ator",
  instrument: "Instrumento",
  geological: "Geológico",
  equipment: "Equipamento",
  analytical: "Analítico",
};

/* F7: ontological_role palette + labels (BFO-like axis, see docs/ONTOLOGY_LAYERS.md) */
const ROLE_COLORS = {
  well_anchor: "#2E86AB",
  well_operation: "#E67E22",
  artifact_primary: "#16A085",
  feature_observation: "#27AE60",
  interpretation_process: "#9B59B6",
  engineering_artifact: "#34495E",
  regulatory_anchor: "#C0392B",
  organizational_actor: "#E74C3C",
  domain_anchor: "#D4A017",
  well_attribute_concept: "#7F8C8D",
  equipment: "#F39C12",
  governance_artifact: "#8E44AD",
  kpi_metric: "#E91E63",
  lifecycle_state: "#3498DB",
  lifecycle_outcome: "#1ABC9C",
  dataset_concept: "#5D4037",
  signal_concept: "#FF5722",
  event_observation: "#FFC107",
  unclassified: "#BDBDBD",
};
const ROLE_LABELS = {
  well_anchor: "Poço (âncora)",
  well_operation: "Operação",
  artifact_primary: "Artefato primário",
  feature_observation: "Feature geológica",
  interpretation_process: "Interpretação",
  engineering_artifact: "Engenharia",
  regulatory_anchor: "Regulatório",
  organizational_actor: "Ator",
  domain_anchor: "Domínio",
  well_attribute_concept: "Atributo do poço",
  equipment: "Equipamento",
  governance_artifact: "Governança",
  kpi_metric: "KPI",
  lifecycle_state: "Ciclo de vida (estado)",
  lifecycle_outcome: "Ciclo de vida (resultado)",
  dataset_concept: "Dataset",
  signal_concept: "Sinal",
  event_observation: "Evento",
  unclassified: "Não classificado",
};
const ROLE_FALLBACK = "#BDBDBD";

function roleColor(role) {
  return ROLE_COLORS[role] || ROLE_FALLBACK;
}
function roleLabel(role) {
  return ROLE_LABELS[role] || role || "não classificado";
}

const LAYERS = {
  layer1: { name: "L1 GeoCore", bg: "#EEEDFE", text: "#3C3489" },
  layer2: { name: "L2 O3PO", bg: "#E1F5EE", text: "#085041" },
  layer3: { name: "L3 PetroKGraph", bg: "#E6F1FB", text: "#042C53" },
  layer4: { name: "L4 OSDU", bg: "#F1EFE8", text: "#2C2C2A" },
  layer5: { name: "L5 ANP", bg: "#EAF3DE", text: "#173404" },
  layer6: { name: "L6 Petrobras", bg: "#FCEBDA", text: "#6B3208" },
};

// ---------- Helpers -------------------------------------------------------

function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

function nonEmpty(arr) {
  return Array.isArray(arr) && arr.length > 0;
}

function groupBy(items, keyFn) {
  const map = new Map();
  for (const item of items) {
    const key = keyFn(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return map;
}

function typeColor(type) {
  return TYPE_COLORS[type] || "#777";
}

function typeLabel(type) {
  return TYPE_LABELS[type] || type || "outro";
}

// ---------- HTML fragments ------------------------------------------------

function renderTypePill(type) {
  const color = typeColor(type);
  const label = typeLabel(type);
  return `<span class="pill" style="--pill-color:${color}">${escapeHtml(label)}</span>`;
}

function renderBadgeList(items, className = "badge") {
  if (!nonEmpty(items)) return "";
  return items.map((item) => `<span class="${className}">${escapeHtml(item)}</span>`).join("");
}

function renderCodeChips(items) {
  if (!nonEmpty(items)) return "";
  return items.map((item) => `<code class="chip">${escapeHtml(item)}</code>`).join("");
}

function renderLayerBadges(layers) {
  if (!nonEmpty(layers)) return "";
  return layers
    .map((key) => {
      const meta = LAYERS[key];
      if (!meta) return `<span class="layer-badge">${escapeHtml(key)}</span>`;
      return `<span class="layer-badge" style="background:${meta.bg};color:${meta.text}">${escapeHtml(meta.name)}</span>`;
    })
    .join("");
}

function renderRow(label, html) {
  if (!html) return "";
  return `
        <div class="row">
          <div class="row-label">${escapeHtml(label)}</div>
          <div class="row-value">${html}</div>
        </div>`;
}

function renderRelations(relations, direction, nodeIndex) {
  if (!nonEmpty(relations)) return "";
  const items = relations
    .map((rel) => {
      const otherId = direction === "out" ? rel.target : rel.source;
      const other = nodeIndex.get(otherId);
      const otherLabel = other ? other.label : otherId;
      const verbPt = rel.relation_label_pt || rel.relation || "";
      const verbEn = rel.relation_label_en
        ? ` <em class="muted">(${escapeHtml(rel.relation_label_en)})</em>`
        : "";
      const arrow = direction === "out" ? "→" : "←";
      const link = `<a href="#entity-${escapeAttr(otherId)}" class="rel-link">${escapeHtml(otherLabel)}</a>`;
      return `<li><span class="rel-verb">${escapeHtml(verbPt)}</span>${verbEn} <span class="rel-arrow">${arrow}</span> ${link}</li>`;
    })
    .join("");
  return `<ul class="rel-list">${items}</ul>`;
}

function renderExternalLinks(node) {
  const parts = [];
  if (node.petrokgraph_uri) {
    parts.push(
      `<li><span class="ext-label">PetroKGraph</span> <a href="${escapeAttr(node.petrokgraph_uri)}" target="_blank" rel="noopener">${escapeHtml(node.petrokgraph_uri)}</a></li>`
    );
  }
  if (node.owl_uri) {
    parts.push(
      `<li><span class="ext-label">OSDU OWL Class</span> <a href="${escapeAttr(node.owl_uri)}" target="_blank" rel="noopener">${escapeHtml(node.owl_uri)}</a></li>`
    );
  }
  if (node.osdu_kind) {
    parts.push(
      `<li><span class="ext-label">OSDU kind</span> <code class="chip">${escapeHtml(node.osdu_kind)}</code></li>`
    );
  }
  if (parts.length === 0) return "";
  return `<ul class="ext-list">${parts.join("")}</ul>`;
}

function renderCard(node, edgesOut, edgesIn, nodeIndex) {
  const id = `entity-${node.id}`;
  const labelEn = node.label_en
    ? ` <span class="label-en">${escapeHtml(node.label_en)}</span>`
    : "";
  const defEn = node.definition_en_canonical
    ? `<p class="def-en">${escapeHtml(node.definition_en_canonical)}</p>`
    : "";
  const def = node.definition ? `<p class="def">${escapeHtml(node.definition)}</p>` : "";
  const legal = node.legal_source
    ? `<span class="legal-source">${escapeHtml(node.legal_source)}</span>`
    : "";

  // Search index (lower-case haystack stored in a data attribute)
  const haystack = [
    node.label,
    node.label_en,
    node.id,
    ...(node.synonyms_pt || []),
    ...(node.synonyms_en || []),
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  const role = node.ontological_role || "unclassified";
  const rolePill = `<span class="pill pill-role" style="--pill-color:${roleColor(role)}">${escapeHtml(roleLabel(role))}</span>`;
  return `
      <section class="card" id="${escapeAttr(id)}" data-type="${escapeAttr(node.type || "")}" data-ontological-role="${escapeAttr(role)}" data-search="${escapeAttr(haystack)}">
        <header class="card-header">
          <h2 class="card-title">
            ${escapeHtml(node.label || node.id)}${labelEn}
          </h2>
          <div class="card-meta">
            ${renderTypePill(node.type)}
            ${rolePill}
            ${legal}
            <a class="card-anchor" href="#${escapeAttr(id)}" title="Permalink">#</a>
          </div>
        </header>
        ${def}
        ${defEn}
        <div class="rows">
          ${renderRow("Sinônimos (PT)", renderBadgeList(node.synonyms_pt, "badge"))}
          ${renderRow("Sinônimos (EN)", renderBadgeList(node.synonyms_en, "badge badge-en"))}
          ${renderRow("Exemplos", renderCodeChips(node.examples))}
          ${renderRow("Datasets", renderBadgeList(node.datasets, "badge badge-dataset"))}
          ${renderRow("Camadas semânticas", renderLayerBadges(node.geocoverage))}
          ${renderRow("Relações de saída", renderRelations(edgesOut, "out", nodeIndex))}
          ${renderRow("Relações de entrada", renderRelations(edgesIn, "in", nodeIndex))}
          ${renderRow("Links externos", renderExternalLinks(node))}
        </div>
      </section>`;
}

function renderSidebar(nodesByType) {
  const orderedTypes = Object.keys(TYPE_COLORS)
    .filter((t) => nodesByType.has(t))
    .concat([...nodesByType.keys()].filter((t) => !(t in TYPE_COLORS)));

  const groups = orderedTypes
    .map((type) => {
      const nodes = nodesByType.get(type);
      nodes.sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id, "pt"));
      const items = nodes
        .map(
          (n) => `
            <li>
              <a href="#entity-${escapeAttr(n.id)}" data-search="${escapeAttr((n.label + " " + (n.label_en || "")).toLowerCase())}">
                <span class="dot" style="background:${typeColor(n.type)}"></span>${escapeHtml(n.label || n.id)}
              </a>
            </li>`
        )
        .join("");
      return `
        <div class="toc-group" data-type="${escapeAttr(type)}">
          <h3 class="toc-heading">
            <span class="dot" style="background:${typeColor(type)}"></span>${escapeHtml(typeLabel(type))}
            <span class="toc-count">${nodes.length}</span>
          </h3>
          <ul class="toc-list">${items}
          </ul>
        </div>`;
    })
    .join("");

  return groups;
}

/* F7: parallel sidebar grouped by ontological_role. */
function renderRoleSidebar(nodesByRole) {
  const orderedRoles = Object.keys(ROLE_COLORS)
    .filter((r) => nodesByRole.has(r))
    .concat([...nodesByRole.keys()].filter((r) => !(r in ROLE_COLORS)));

  return orderedRoles
    .map((role) => {
      const nodes = nodesByRole.get(role);
      nodes.sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id, "pt"));
      const items = nodes
        .map(
          (n) => `
            <li>
              <a href="#entity-${escapeAttr(n.id)}" data-search="${escapeAttr((n.label + " " + (n.label_en || "")).toLowerCase())}">
                <span class="dot" style="background:${roleColor(role)}"></span>${escapeHtml(n.label || n.id)}
              </a>
            </li>`
        )
        .join("");
      return `
        <div class="toc-group" data-role="${escapeAttr(role)}">
          <h3 class="toc-heading">
            <span class="dot" style="background:${roleColor(role)}"></span>${escapeHtml(roleLabel(role))}
            <span class="toc-count">${nodes.length}</span>
          </h3>
          <ul class="toc-list">${items}
          </ul>
        </div>`;
    })
    .join("");
}

// ---------- Static CSS / JS ----------------------------------------------

const CSS = `
:root {
  --bg: #ffffff;
  --bg-alt: #f7f8fa;
  --bg-card: #ffffff;
  --fg: #1f2329;
  --fg-muted: #5a6068;
  --border: #e3e6ea;
  --border-strong: #c9ced4;
  --accent: #378ADD;
  --shadow: 0 1px 2px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.04);
  --radius: 10px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15181d;
    --bg-alt: #1c2026;
    --bg-card: #1a1e24;
    --fg: #e6e9ee;
    --fg-muted: #9aa3ad;
    --border: #2a2f37;
    --border-strong: #3a414b;
    --accent: #7ab2eb;
    --shadow: 0 1px 2px rgba(0,0,0,.3), 0 6px 18px rgba(0,0,0,.4);
  }
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg);
  color: var(--fg);
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header */
.site-header {
  position: sticky; top: 0; z-index: 50;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  padding: 10px 18px;
  display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
}
.site-header h1 {
  font-size: 16px; margin: 0; font-weight: 600;
  letter-spacing: -.01em;
}
.site-header .ext-links {
  display: flex; gap: 12px; flex-wrap: wrap; margin-left: auto;
  font-size: 13px;
}
.site-header .ext-links a {
  padding: 5px 10px; border: 1px solid var(--border); border-radius: 6px;
  color: var(--fg);
}
.site-header .ext-links a:hover { background: var(--bg-alt); text-decoration: none; }
.site-header .search-wrap {
  flex: 1 1 240px; min-width: 200px; max-width: 380px;
}
.site-header input[type="search"] {
  width: 100%; padding: 7px 10px;
  font: inherit;
  border: 1px solid var(--border-strong);
  border-radius: 6px;
  background: var(--bg-alt);
  color: var(--fg);
}
.site-header input[type="search"]:focus {
  outline: 2px solid var(--accent); outline-offset: -1px;
}

/* Layout */
.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 0;
  max-width: 1400px;
  margin: 0 auto;
}
.sidebar {
  position: sticky; top: 56px;
  align-self: start;
  height: calc(100vh - 56px);
  overflow-y: auto;
  border-right: 1px solid var(--border);
  padding: 14px 12px 24px 14px;
  background: var(--bg);
}
.toc-group { margin-bottom: 14px; }
.toc-heading {
  font-size: 11px; text-transform: uppercase; letter-spacing: .06em;
  color: var(--fg-muted);
  margin: 8px 0 6px;
  display: flex; align-items: center; gap: 6px;
  font-weight: 600;
}
.toc-count {
  margin-left: auto;
  background: var(--bg-alt); color: var(--fg-muted);
  border-radius: 10px; padding: 1px 7px; font-size: 10px;
}
.toc-list { list-style: none; margin: 0; padding: 0; }
.toc-list li a {
  display: flex; align-items: center; gap: 7px;
  padding: 4px 8px;
  border-radius: 5px;
  color: var(--fg);
  font-size: 13px;
}
.toc-list li a:hover { background: var(--bg-alt); text-decoration: none; }
.toc-list li a.hidden { display: none; }
.dot {
  display: inline-block; width: 8px; height: 8px;
  border-radius: 50%; flex: 0 0 8px;
}

/* Main */
.main {
  padding: 22px 28px 60px;
  min-width: 0;
}
.intro {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 22px;
  color: var(--fg-muted);
  font-size: 13px;
}
.intro strong { color: var(--fg); }
.no-match {
  display: none;
  text-align: center; padding: 40px;
  color: var(--fg-muted);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}
.no-match.show { display: block; }

/* Card */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 20px;
  margin-bottom: 22px;
  scroll-margin-top: 70px;
}
.card.hidden { display: none; }
.card-header {
  display: flex; flex-wrap: wrap; gap: 10px; align-items: baseline;
  border-bottom: 1px solid var(--border);
  padding-bottom: 10px;
  margin-bottom: 12px;
}
.card-title {
  font-size: 20px; margin: 0; font-weight: 600;
  letter-spacing: -.01em;
}
.label-en {
  font-size: 14px; font-style: italic; color: var(--fg-muted);
  font-weight: 400; margin-left: 4px;
}
.card-meta {
  margin-left: auto;
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
}
.card-anchor {
  color: var(--fg-muted); font-family: ui-monospace, monospace;
  padding: 2px 6px; border-radius: 4px;
}
.card-anchor:hover { background: var(--bg-alt); }

.pill {
  background: var(--pill-color);
  color: #fff;
  font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
  padding: 3px 9px; border-radius: 999px; font-weight: 600;
}
.legal-source {
  font-size: 11px; color: var(--fg-muted);
  border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 7px;
}
.def {
  font-size: 14.5px; line-height: 1.6;
  margin: 4px 0 6px;
}
.def-en {
  font-style: italic;
  color: var(--fg-muted);
  font-size: 13.5px; line-height: 1.55;
  margin: 0 0 6px;
}

.rows {
  display: grid;
  grid-template-columns: minmax(150px, 200px) 1fr;
  gap: 4px 18px;
  margin-top: 10px;
}
.row {
  display: contents;
}
.row-label {
  color: var(--fg-muted);
  font-size: 12px; text-transform: uppercase; letter-spacing: .04em;
  padding: 8px 0;
  border-top: 1px solid var(--border);
  font-weight: 600;
}
.row-value {
  padding: 8px 0;
  border-top: 1px solid var(--border);
  display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
}
.row:first-child .row-label, .row:first-child .row-value { border-top: 0; }

.badge {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 9px;
  font-size: 12px;
  color: var(--fg);
}
.badge-en { font-style: italic; }
.badge-dataset {
  background: transparent;
  border: 1px dashed var(--border-strong);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11.5px;
}
.layer-badge {
  font-size: 11px; font-weight: 600;
  padding: 3px 9px;
  border-radius: 4px;
  letter-spacing: .02em;
}
.chip {
  background: var(--bg-alt);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 7px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}

.rel-list, .ext-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 4px;
  width: 100%;
}
.rel-list li, .ext-list li {
  font-size: 13px;
}
.rel-verb {
  color: var(--fg);
  font-weight: 500;
}
.rel-arrow {
  color: var(--fg-muted); font-family: ui-monospace, monospace;
  margin: 0 4px;
}
.rel-link {
  font-weight: 500;
}
.muted { color: var(--fg-muted); font-size: 12px; }
.ext-label {
  display: inline-block;
  min-width: 130px;
  font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
  color: var(--fg-muted);
  font-weight: 600;
}

/* Mobile */
@media (max-width: 768px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: static;
    height: auto;
    max-height: 280px;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
  .main { padding: 16px; }
  .rows { grid-template-columns: 1fr; gap: 0; }
  .row-label { padding: 8px 0 2px; border-top: 1px solid var(--border); }
  .row-value { padding: 0 0 8px; border-top: 0; }
  .row:first-child .row-value { border-top: 0; }
  .site-header h1 { width: 100%; }
  .site-header .ext-links { margin-left: 0; }
  .card-meta { margin-left: 0; }
}
`;

/* F7-only CSS — opt-in via buildCardsHtml. NOT inlined into buildGsoCardsHtml
   because gso-cards.html has no .pill-role, .color-mode-seg or .sidebar-group
   elements, so these rules would be inert bytes there. */
const F7_CSS = `
/* F7: secondary pill for ontological_role — softer outline style so it doesn't fight the type pill */
.pill-role {
  background: transparent;
  color: var(--pill-color);
  border: 1px solid var(--pill-color);
}

/* F7: "Cor por" segmented toggle (mirrors index.html) */
.color-mode {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 11px; color: var(--fg-muted);
  text-transform: uppercase; letter-spacing: .04em;
}
.color-mode-seg {
  display: inline-flex; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden;
}
.color-mode-seg button {
  background: transparent; border: 0; cursor: pointer;
  color: var(--fg-muted); font: inherit;
  padding: 4px 10px; transition: background 120ms ease, color 120ms ease;
}
.color-mode-seg button + button { border-left: 1px solid var(--border-strong); }
.color-mode-seg button:hover { color: var(--fg); }
.color-mode-seg button.is-active { background: var(--bg-alt); color: var(--fg); }

/* F7: show only the sidebar that matches the active mode */
.sidebar-group { display: none; }
body[data-color-mode="type"] .sidebar-group[data-mode="type"] { display: block; }
body[data-color-mode="role"] .sidebar-group[data-mode="role"] { display: block; }
body[data-color-mode="role"] .pill-role { background: var(--pill-color); color: #fff; }
body[data-color-mode="role"] .pill:not(.pill-role) {
  background: transparent; color: var(--pill-color); border: 1px solid var(--pill-color);
}
`;

const CLIENT_JS = `
(function () {
  const input = document.getElementById('search-input');
  const cards = Array.from(document.querySelectorAll('.card'));
  const tocLinks = Array.from(document.querySelectorAll('.toc-list li a'));
  const tocGroups = Array.from(document.querySelectorAll('.toc-group'));
  const noMatch = document.getElementById('no-match');

  function applyFilter(q) {
    const query = (q || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(c => {
      const hay = c.getAttribute('data-search') || '';
      const match = !query || hay.indexOf(query) !== -1;
      c.classList.toggle('hidden', !match);
      if (match) visible++;
    });
    tocLinks.forEach(a => {
      const hay = a.getAttribute('data-search') || '';
      const match = !query || hay.indexOf(query) !== -1;
      a.classList.toggle('hidden', !match);
    });
    tocGroups.forEach(g => {
      const anyVisible = g.querySelectorAll('.toc-list li a:not(.hidden)').length > 0;
      g.style.display = anyVisible ? '' : 'none';
    });
    if (noMatch) noMatch.classList.toggle('show', visible === 0);
  }

  if (input) {
    input.addEventListener('input', e => applyFilter(e.target.value));
    input.addEventListener('keydown', e => {
      if (e.key === 'Escape') { input.value = ''; applyFilter(''); }
    });
  }

  // Smooth-scroll TOC clicks (don't fight native anchor jump on mobile)
  tocLinks.forEach(a => {
    a.addEventListener('click', e => {
      const href = a.getAttribute('href');
      if (!href || href[0] !== '#') return;
      const el = document.querySelector(href);
      if (el) {
        e.preventDefault();
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', href);
      }
    });
  });
})();
`;

/* F7-only client JS — opt-in via buildCardsHtml. NOT inlined into
   buildGsoCardsHtml because gso-cards.html has no #color-mode-seg button
   to wire up. Self-invoking IIFE to keep its scope local. */
const F7_JS = `
(function () {
  const modeButtons = Array.from(document.querySelectorAll('#color-mode-seg button'));
  if (!modeButtons.length) return;
  function setColorMode(mode) {
    if (mode !== 'type' && mode !== 'role') return;
    document.body.dataset.colorMode = mode;
    modeButtons.forEach(b => {
      const active = b.dataset.mode === mode;
      b.classList.toggle('is-active', active);
      b.setAttribute('aria-selected', active ? 'true' : 'false');
    });
  }
  modeButtons.forEach(b => b.addEventListener('click', () => setColorMode(b.dataset.mode)));
  if (!document.body.dataset.colorMode) document.body.dataset.colorMode = 'type';
})();
`;

// ---------- Public entry --------------------------------------------------

export function buildCardsHtml(graph) {
  const nodes = Array.isArray(graph?.nodes) ? graph.nodes.slice() : [];
  const edges = Array.isArray(graph?.edges)
    ? graph.edges
    : Array.isArray(graph?.links)
      ? graph.links
      : [];

  // Sort nodes by label for stable output
  nodes.sort((a, b) => (a.label || a.id || "").localeCompare(b.label || b.id || "", "pt"));

  // Index for fast lookup, edges out/in per node
  const nodeIndex = new Map(nodes.map((n) => [n.id, n]));
  const outByNode = new Map();
  const inByNode = new Map();
  for (const n of nodes) {
    outByNode.set(n.id, []);
    inByNode.set(n.id, []);
  }
  for (const e of edges) {
    const s = typeof e.source === "object" ? e.source.id : e.source;
    const t = typeof e.target === "object" ? e.target.id : e.target;
    if (outByNode.has(s)) outByNode.get(s).push({ ...e, source: s, target: t });
    if (inByNode.has(t)) inByNode.get(t).push({ ...e, source: s, target: t });
  }

  // Group nodes by type for sidebar
  const byType = groupBy(nodes, (n) => n.type || "other");
  // F7: parallel grouping by ontological_role
  const byRole = groupBy(nodes, (n) => n.ontological_role || "unclassified");

  // Render
  // Collapse runs of whitespace between tags to keep the output compact
  // without changing rendered semantics.
  const compact = (s) => s.replace(/>\s+</g, "><").replace(/\s{2,}/g, " ");

  const cardsHtml = nodes
    .map((n) =>
      compact(renderCard(n, outByNode.get(n.id) || [], inByNode.get(n.id) || [], nodeIndex))
    )
    .join("\n");

  const sidebarHtml = compact(renderSidebar(byType));
  const sidebarRoleHtml = compact(renderRoleSidebar(byRole));

  const generated = graph?.generated || new Date().toISOString();
  const totalNodes = nodes.length;
  const totalEdges = edges.length;

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GeoBrain — Entity Cards</title>
  <meta name="description" content="Cartões navegáveis das entidades do GeoBrain, no estilo da documentação OWL gerada pelo pyLODE.">
  <style>${CSS}${F7_CSS}</style>
</head>
<body data-color-mode="type">
  <header class="site-header">
    <h1>GeoBrain <span style="color:var(--fg-muted);font-weight:400">— Entity Cards</span></h1>
    <div class="search-wrap">
      <input id="search-input" type="search" placeholder="Buscar por rótulo, sinônimo ou ID…" autocomplete="off" spellcheck="false">
    </div>
    <div class="color-mode" aria-label="Cor por">
      <span>Cor por</span>
      <div class="color-mode-seg" id="color-mode-seg" role="tablist">
        <button type="button" class="is-active" data-mode="type" role="tab" aria-selected="true" title="Agrupar por tipo">Tipo</button>
        <button type="button" data-mode="role" role="tab" aria-selected="false" title="Agrupar por papel ontológico (BFO-like)">Papel ontológico</button>
      </div>
    </div>
    <nav class="ext-links" aria-label="Visualizações">
      <a href="index.html" title="Visão de grafo D3 force-directed">Grafo D3</a>
      <a href="gso-cards.html" title="Cards das classes GSO/Loop3D (camada 7)">GSO L7</a>
      <a href="data/geobrain.ttl" title="Ontologia em Turtle">TTL</a>
      <a href="https://service.tib.eu/webvowl/#iri=https://thiagoflc.github.io/geobrain/data/geobrain.ttl" target="_blank" rel="noopener" title="Visualizar OWL no WebVOWL">WebVOWL</a>
    </nav>
  </header>

  <div class="layout">
    <aside class="sidebar" aria-label="Sumário">
      <div class="sidebar-group" data-mode="type">
        ${sidebarHtml}
      </div>
      <div class="sidebar-group" data-mode="role">
        ${sidebarRoleHtml}
      </div>
    </aside>

    <main class="main">
      <div class="intro">
        <strong>${totalNodes}</strong> entidades · <strong>${totalEdges}</strong> relações ·
        gerado em <code>${escapeHtml(generated)}</code>.
        Cada cartão lista a definição, sinônimos PT/EN, exemplos, datasets, camadas semânticas e relações de entrada/saída.
        Use a busca para filtrar por rótulo ou sinônimo.
      </div>

      <div id="no-match" class="no-match">Nenhuma entidade corresponde à busca.</div>

      ${cardsHtml}
    </main>
  </div>

  <script>${CLIENT_JS}</script>
  <script>${F7_JS}</script>
</body>
</html>
`;
}

export default buildCardsHtml;

/* ─────────────────────────────────────────────────────────────
 * GSO cards — pyLODE-style page for Layer 7 (Loop3D Geoscience Ontology)
 *
 * Input: array of modules from loadGsoModules() in generate.js, each:
 *   { meta: { module, base_uri, class_count, license, attribution },
 *     classes: { "gso:Foo": { gso_class, owl_uri, pref_label_en, ... }, ... } }
 *
 * Output: standalone HTML string for gso-cards.html. Reuses CSS/CLIENT_JS.
 * ───────────────────────────────────────────────────────────── */

const GSO_MODULE_LABELS = {
  "GSO-Geologic_Structure_Fault": "Falhas",
  "GSO-Geologic_Structure_Fold": "Dobras",
  "GSO-Geologic_Structure_Foliation": "Foliação",
  "GSO-Geologic_Structure_Lineation": "Lineação",
  "GSO-Geologic_Structure_Contact": "Contatos",
};

const GSO_MODULE_COLORS = {
  "GSO-Geologic_Structure_Fault": "#D85A30",
  "GSO-Geologic_Structure_Fold": "#C77B30",
  "GSO-Geologic_Structure_Foliation": "#7F77DD",
  "GSO-Geologic_Structure_Lineation": "#378ADD",
  "GSO-Geologic_Structure_Contact": "#639922",
};

function gsoModuleLabel(m) {
  return GSO_MODULE_LABELS[m] || m.replace(/^GSO-Geologic_Structure_/, "");
}

function gsoModuleColor(m) {
  return GSO_MODULE_COLORS[m] || "#777";
}

function renderGsoCard(c, moduleName, indexByCurie) {
  const id = `gso-${c.gso_class}`;
  const titleFr = c.pref_label_fr
    ? ` <span class="label-en">${escapeHtml(c.pref_label_fr)} (fr)</span>`
    : "";
  const def = c.definition_en_canonical
    ? `<p class="def-en">${escapeHtml(c.definition_en_canonical)}</p>`
    : "";
  const parents = (c.parents || [])
    .map((p) => {
      const localName = p.includes(":") ? p.split(":")[1] : p;
      const target = indexByCurie.get(p) || indexByCurie.get(localName);
      if (target)
        return `<a class="badge badge-rel" href="#gso-${escapeAttr(target.gso_class)}">${escapeHtml(p)}</a>`;
      return `<span class="badge" title="External or unresolved CURIE">${escapeHtml(p)}</span>`;
    })
    .join("");
  const sources = renderBadgeList(c.sources || [], "badge badge-dataset");
  const owlLink = c.owl_uri
    ? `<a class="badge badge-en" href="${escapeAttr(c.owl_uri)}" target="_blank" rel="noopener">${escapeHtml(c.owl_uri)}</a>`
    : "";
  const haystack = [c.gso_class, c.pref_label_en, c.pref_label_fr, ...(c.parents || [])]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  const color = gsoModuleColor(moduleName);
  const modLabel = gsoModuleLabel(moduleName);

  return `
      <section class="card" id="${escapeAttr(id)}" data-type="${escapeAttr(moduleName)}" data-search="${escapeAttr(haystack)}">
        <header class="card-header">
          <h2 class="card-title">
            ${escapeHtml(c.pref_label_en || c.gso_class)}${titleFr}
          </h2>
          <div class="card-meta">
            <span class="pill" style="--pill-color:${color}">${escapeHtml(modLabel)}</span>
            <span class="legal-source">CC BY 4.0</span>
            <a class="card-anchor" href="#${escapeAttr(id)}" title="Permalink">#</a>
          </div>
        </header>
        ${def}
        <div class="rows">
          ${renderRow("GSO class", `<code>${escapeHtml(c.gso_class)}</code>`)}
          ${renderRow("OWL URI", owlLink)}
          ${renderRow("Subclasse de", parents)}
          ${renderRow("Fonte original", sources)}
          ${renderRow("Atribuição", `<span class="badge">${escapeHtml(c.attribution || "")}</span>`)}
        </div>
      </section>`;
}

function renderGsoSidebar(byModule) {
  const order = Object.keys(GSO_MODULE_LABELS).filter((m) => byModule.has(m));
  return order
    .map((m) => {
      const list = byModule
        .get(m)
        .slice()
        .sort((a, b) =>
          (a.pref_label_en || a.gso_class).localeCompare(b.pref_label_en || b.gso_class, "en")
        );
      const items = list
        .map(
          (c) => `
            <li>
              <a href="#gso-${escapeAttr(c.gso_class)}" data-search="${escapeAttr((c.pref_label_en || c.gso_class).toLowerCase())}">
                <span class="dot" style="background:${gsoModuleColor(m)}"></span>${escapeHtml(c.pref_label_en || c.gso_class)}
              </a>
            </li>`
        )
        .join("");
      return `
        <div class="toc-group" data-type="${escapeAttr(m)}">
          <h3 class="toc-heading">
            <span class="dot" style="background:${gsoModuleColor(m)}"></span>${escapeHtml(gsoModuleLabel(m))}
            <span class="toc-count">${list.length}</span>
          </h3>
          <ul class="toc-list">${items}
          </ul>
        </div>`;
    })
    .join("");
}

export function buildGsoCardsHtml(modules) {
  const all = [];
  const indexByCurie = new Map();
  for (const mod of modules) {
    for (const [curie, c] of Object.entries(mod.classes)) {
      const enriched = {
        ...c,
        _curie: curie,
        _module: mod.meta.module,
        attribution: mod.meta.attribution,
      };
      all.push(enriched);
      indexByCurie.set(curie, enriched);
      indexByCurie.set(c.gso_class, enriched);
    }
  }
  all.sort((a, b) =>
    (a.pref_label_en || a.gso_class).localeCompare(b.pref_label_en || b.gso_class, "en")
  );

  const byModule = groupBy(all, (c) => c._module);
  const compact = (s) => s.replace(/>\s+</g, "><").replace(/\s{2,}/g, " ");
  const cardsHtml = all.map((c) => compact(renderGsoCard(c, c._module, indexByCurie))).join("\n");
  const sidebarHtml = compact(renderGsoSidebar(byModule));
  const generated = new Date().toISOString();

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GeoBrain — GSO (Layer 7) Cards</title>
  <meta name="description" content="Cartões navegáveis das classes da Geoscience Ontology (Loop3D, Brodaric & Richard 2021), camada 7 do GeoBrain.">
  <style>${CSS}</style>
</head>
<body>
  <header class="site-header">
    <h1>GeoBrain <span style="color:var(--fg-muted);font-weight:400">— GSO L7 Cards</span></h1>
    <div class="search-wrap">
      <input id="search-input" type="search" placeholder="Buscar por classe, label EN ou CURIE…" autocomplete="off" spellcheck="false">
    </div>
    <nav class="ext-links" aria-label="Navegação">
      <a href="index.html" title="Visão de grafo D3 force-directed">Grafo</a>
      <a href="index-cards.html" title="Cards das entidades L1-L6">Entity Cards</a>
      <a href="https://github.com/Loop3D/GKM" target="_blank" rel="noopener" title="Repositório GKM">GKM</a>
    </nav>
  </header>

  <div class="layout">
    <aside class="sidebar" aria-label="Sumário">
      ${sidebarHtml}
    </aside>

    <main class="main">
      <div class="intro">
        <strong>${all.length}</strong> classes GSO em <strong>${byModule.size}</strong> módulos estruturais ·
        gerado em <code>${escapeHtml(generated)}</code>.
        Importado de <a href="https://github.com/Loop3D/GKM" target="_blank" rel="noopener">Loop3D/GKM</a>
        (Brodaric &amp; Richard 2021, GSC OF 8796, <a href="https://doi.org/10.4095/328296" target="_blank" rel="noopener">DOI 10.4095/328296</a>, CC BY 4.0).
        Cobre falhas, dobras, foliação, lineação e contatos — gap estrutural complementar a OSDU/ontopetro.
      </div>

      <div id="no-match" class="no-match">Nenhuma classe corresponde à busca.</div>

      ${cardsHtml}
    </main>
  </div>

  <script>${CLIENT_JS}</script>
</body>
</html>
`;
}
