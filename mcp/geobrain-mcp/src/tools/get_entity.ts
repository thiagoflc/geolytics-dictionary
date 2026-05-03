/**
 * get_entity — returns a single entity from entity-graph.json with all
 * outgoing and incoming relations resolved to full neighbor objects.
 */

import { z } from "zod";
import { entityGraph, EntityNode, EntityEdge } from "../data.js";

export const schema = z.object({
  id: z.string().min(1).describe("Entity id (e.g. 'poco', 'bacia-sedimentar', 'operador')"),
});

type Input = z.infer<typeof schema>;

function nodeIndex(): Map<string, EntityNode> {
  const m = new Map<string, EntityNode>();
  for (const n of entityGraph.nodes) m.set(n.id, n);
  return m;
}

let _nodeIdx: Map<string, EntityNode> | null = null;
function getNodeIndex(): Map<string, EntityNode> {
  if (!_nodeIdx) _nodeIdx = nodeIndex();
  return _nodeIdx;
}

export function execute(input: Input): string {
  const idx = getNodeIndex();
  const node = idx.get(input.id);

  if (!node) {
    const candidates = entityGraph.nodes
      .filter(
        (n) =>
          (n.id ?? "").toLowerCase().includes(input.id.toLowerCase()) ||
          (n.label ?? "").toLowerCase().includes(input.id.toLowerCase())
      )
      .slice(0, 5)
      .map((n) => ({ id: n.id, label: n.label }));

    return JSON.stringify({
      found: false,
      id: input.id,
      candidates,
    });
  }

  const outgoing: Array<{
    relation: string;
    relation_label_pt?: string;
    relation_label_en?: string;
    target: EntityNode;
  }> = [];
  const incoming: Array<{
    relation: string;
    relation_label_pt?: string;
    relation_label_en?: string;
    source: EntityNode;
  }> = [];

  for (const edge of entityGraph.edges) {
    if (edge.source === node.id) {
      const target = idx.get(edge.target);
      if (target) {
        outgoing.push({
          relation: edge.relation,
          relation_label_pt: edge.relation_label_pt,
          relation_label_en: edge.relation_label_en,
          target,
        });
      }
    }
    if (edge.target === node.id) {
      const source = idx.get(edge.source);
      if (source) {
        incoming.push({
          relation: edge.relation,
          relation_label_pt: edge.relation_label_pt,
          relation_label_en: edge.relation_label_en,
          source,
        });
      }
    }
  }

  return JSON.stringify(
    {
      found: true,
      entity: node,
      outgoing,
      incoming,
    },
    null,
    2
  );
}
