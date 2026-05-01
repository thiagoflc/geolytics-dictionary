#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'build', 'neo4j');

const TYPE_LABEL = {
  operational: 'Operational',
  geological: 'Geological',
  contractual: 'Contractual',
  actor: 'Actor',
  instrument: 'Instrument',
  equipment: 'Equipment',
  analytical: 'Analytical',
};

function esc(s) {
  if (s == null) return 'null';
  return "'" + String(s).replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";
}

function escArr(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return '[]';
  return '[' + arr.map(esc).join(', ') + ']';
}

function propMap(obj) {
  return Object.entries(obj)
    .filter(([, v]) => v != null && v !== '' && !(Array.isArray(v) && v.length === 0))
    .map(([k, v]) => {
      if (Array.isArray(v)) return `${k}: ${escArr(v)}`;
      if (typeof v === 'boolean') return `${k}: ${v}`;
      if (typeof v === 'number') return `${k}: ${v}`;
      return `${k}: ${esc(v)}`;
    })
    .join(', ');
}

const lines = { nodes: [], rels: [] };

function nodeId(id) {
  return 'n_' + id.replace(/[^a-zA-Z0-9_]/g, '_');
}

function emitNode(varName, labels, props) {
  const labelStr = labels.map(l => `:${l}`).join('');
  const p = propMap(props);
  lines.nodes.push(`MERGE (${varName}${labelStr} {id: ${esc(props.id)}})`);
  if (p) {
    lines.nodes.push(`  ON CREATE SET ${varName} += {${p}}`);
    lines.nodes.push(`  ON MATCH SET ${varName} += {${p}}`);
  }
  lines.nodes.push('');
}

function emitRel(fromId, toId, relType, props) {
  const fromVar = nodeId(fromId);
  const toVar = nodeId(toId);
  const safeName = relType.toUpperCase();
  const p = props && Object.keys(props).length > 0 ? ' {' + propMap(props) + '}' : '';
  lines.rels.push(
    `MATCH (${fromVar} {id: ${esc(fromId)}}), (${toVar} {id: ${esc(toId)}})`,
    `MERGE (${fromVar})-[:${safeName}${p}]->(${toVar})`,
    ''
  );
}

const entityGraph = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'entity-graph.json'), 'utf8'));
const ontopetro = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'ontopetro.json'), 'utf8'));
const crosswalk = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'osdu-gso-crosswalk.json'), 'utf8'));

const GSO_FILES = ['gso-faults', 'gso-folds', 'gso-foliations', 'gso-lineations', 'gso-contacts'];
const gsoData = GSO_FILES.map(f => ({
  module: f,
  data: JSON.parse(fs.readFileSync(path.join(ROOT, 'data', `${f}.json`), 'utf8')),
}));

entityGraph.nodes.forEach(node => {
  const typeLabel = TYPE_LABEL[node.type] || 'Entity';
  const props = {
    id: node.id,
    label: node.label,
    label_en: node.label_en || null,
    type: node.type,
    definition: node.definition || null,
    petrokgraph_uri: node.petrokgraph_uri || null,
    osdu_kind: node.osdu_kind || null,
    geosciml_uri: node.geosciml_uri || null,
    owl_uri: node.owl_uri || null,
    geocoverage: node.geocoverage || [],
    sources: node.legal_source ? [node.legal_source] : [],
  };
  emitNode(nodeId(node.id), ['Entity', typeLabel], props);
});

entityGraph.edges.forEach(edge => {
  emitRel(edge.source, edge.target, edge.relation, {
    label_pt: edge.relation_label_pt || null,
    label_en: edge.relation_label_en || null,
    style: edge.style || null,
  });
});

ontopetro.classes.forEach(cls => {
  const nid = `ontopetro_class_${cls.id}`;
  emitNode(nodeId(nid), ['OntologyClass'], {
    id: nid,
    ontopetro_id: cls.id,
    name: cls.name,
    name_en: cls.name_en || null,
    superclass: cls.superclass || null,
    description: cls.description || null,
    domain: cls.domain || null,
    sources: cls.sources || [],
    entity_graph_id: cls.entity_graph_id || null,
  });
  if (cls.entity_graph_id) {
    emitRel(nid, cls.entity_graph_id, 'maps_to_entity', {});
    emitRel(cls.entity_graph_id, nid, 'has_ontology_class', {});
  }
});

ontopetro.relations.forEach(rel => {
  const domainId = `ontopetro_class_${ontopetro.classes.find(c => c.name === rel.domain)?.id || rel.domain}`;
  const rangeId = `ontopetro_class_${ontopetro.classes.find(c => c.name === rel.range)?.id || rel.range}`;
  const domainClass = ontopetro.classes.find(c => c.name === rel.domain);
  const rangeClass = ontopetro.classes.find(c => c.name === rel.range);
  if (domainClass && rangeClass) {
    emitRel(
      `ontopetro_class_${domainClass.id}`,
      `ontopetro_class_${rangeClass.id}`,
      rel.name,
      { cardinality: rel.cardinality || null, description: rel.description || null }
    );
  }
});

ontopetro.instances.forEach(inst => {
  const nid = `ontopetro_inst_${inst.id}`;
  const classNode = ontopetro.classes.find(c => c.name === inst.class);
  const props = {
    id: nid,
    ontopetro_id: inst.id,
    name: inst.name,
    instance_class: inst.class,
    source: inst.source || null,
  };
  if (inst.attributes) {
    Object.entries(inst.attributes).forEach(([k, v]) => {
      if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
        props[k] = v;
      }
    });
  }
  emitNode(nodeId(nid), ['OntologyInstance'], props);
  if (classNode) {
    emitRel(nid, `ontopetro_class_${classNode.id}`, 'instance_of', {});
  }
});

gsoData.forEach(({ module, data }) => {
  Object.entries(data.classes).forEach(([key, cls]) => {
    const nid = `gso_${cls.gso_class}`;
    emitNode(nodeId(nid), ['GSOClass'], {
      id: nid,
      gso_class: cls.gso_class,
      owl_uri: cls.owl_uri || null,
      pref_label_en: cls.pref_label_en || null,
      pref_label_fr: cls.pref_label_fr || null,
      definition_en_canonical: cls.definition_en_canonical || null,
      parents: cls.parents || [],
      sources: cls.sources || [],
      attribution: cls.attribution || null,
      gso_module: module,
    });
    (cls.parents || []).forEach(parentRef => {
      const parentClass = parentRef.replace(/^[a-z]+:/, '');
      const parentId = `gso_${parentClass}`;
      emitRel(nid, parentId, 'subclass_of', {});
    });
  });
});

crosswalk.mappings.forEach(m => {
  const gsoClass = m.gso_class;
  const osduClass = m.osdu_class;
  const gsoId = `gso_${gsoClass}`;
  if (!osduClass) {
    lines.rels.push(
      `// GSO-only: ${gsoClass} (${m.match}) — no OSDU equivalent`,
      ''
    );
    return;
  }
  const osduEntityId = entityGraph.nodes.find(
    n => n.osdu_kind && n.osdu_kind.toLowerCase().includes(osduClass.toLowerCase())
  )?.id;
  lines.rels.push(`// OSDU-GSO crosswalk: ${osduClass} ${m.match} ${gsoClass}`);
  if (osduEntityId) {
    lines.rels.push(
      `MATCH (entity {id: ${esc(osduEntityId)}}), (gso {id: ${esc(gsoId)}})`,
      `MERGE (entity)-[:${m.match.toUpperCase()} {note: ${esc(m.note || null)}}]->(gso)`,
      ''
    );
  } else {
    lines.rels.push(
      `MATCH (gso {id: ${esc(gsoId)}})`,
      `SET gso.osdu_crosswalk_class = ${esc(osduClass)}, gso.osdu_crosswalk_match = ${esc(m.match)}`,
      ''
    );
  }
});

(crosswalk.ontopetro_to_gso || []).forEach(m => {
  const classNode = ontopetro.classes.find(c => c.name === m.ontopetro);
  if (!classNode) return;
  const fromId = `ontopetro_class_${classNode.id}`;
  const gsoClass = m.gso.split('/').pop();
  const toId = `gso_${gsoClass}`;
  lines.rels.push(
    `MATCH (op {id: ${esc(fromId)}}), (gso {id: ${esc(toId)}})`,
    `MERGE (op)-[:${m.match.toUpperCase()}]->(gso)`,
    ''
  );
});

fs.mkdirSync(OUT, { recursive: true });

const nodeHeader = [
  '// Geolytics Dictionary — Neo4j node import',
  `// Generated: ${new Date().toISOString()}`,
  '// Run with: cypher-shell -u neo4j -p <password> --file build/neo4j/nodes.cypher',
  '',
];
fs.writeFileSync(path.join(OUT, 'nodes.cypher'), nodeHeader.join('\n') + lines.nodes.join('\n'));

const relHeader = [
  '// Geolytics Dictionary — Neo4j relationship import',
  `// Generated: ${new Date().toISOString()}`,
  '// Run AFTER nodes.cypher',
  '// Run with: cypher-shell -u neo4j -p <password> --file build/neo4j/relationships.cypher',
  '',
];
fs.writeFileSync(path.join(OUT, 'relationships.cypher'), relHeader.join('\n') + lines.rels.join('\n'));

const nodeCount = lines.nodes.filter(l => l.startsWith('MERGE')).length;
const relCount = lines.rels.filter(l => l.startsWith('MERGE')).length;
console.log(`nodes.cypher      ${lines.nodes.length} lines  (${nodeCount} MERGE statements)`);
console.log(`relationships.cypher  ${lines.rels.length} lines  (${relCount} MERGE statements)`);
