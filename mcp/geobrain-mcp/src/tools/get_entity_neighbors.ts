/**
 * get_entity_neighbors — multi-hop BFS traversal of the entity graph.
 *
 * hops: 1 = direct neighbors only, 2 = neighbors-of-neighbors, etc.
 * edge_types: if provided, only follow edges whose `relation` matches.
 */

import { z } from "zod";
import { entityGraph, EntityNode, EntityEdge } from "../data.js";

export const schema = z.object({
  id: z.string().min(1).describe("Starting entity id"),
  hops: z
    .union([z.literal(1), z.literal(2), z.literal(3)])
    .optional()
    .default(1)
    .describe("Number of hops (1-3). Default 1."),
  edge_types: z
    .array(z.string())
    .optional()
    .describe("Filter by relation type (e.g. ['drilled_in', 'classified_by']). Omit for all."),
});

type Input = z.infer<typeof schema>;

interface NeighborEntry {
  id: string;
  label?: string;
  label_en?: string;
  type?: string;
  via_relation: string;
  direction: "outgoing" | "incoming";
  hop: number;
  petrokgraph_uri?: string;
  osdu_kind?: string | null;
}

export function execute(input: Input): string {
  const nodeIdx = new Map<string, EntityNode>();
  for (const n of entityGraph.nodes) nodeIdx.set(n.id, n);

  if (!nodeIdx.has(input.id)) {
    return JSON.stringify({ found: false, id: input.id });
  }

  const visited = new Set<string>([input.id]);
  const neighbors: NeighborEntry[] = [];
  const frontier = [input.id];

  for (let hop = 1; hop <= input.hops; hop++) {
    const nextFrontier: string[] = [];

    for (const currentId of frontier) {
      for (const edge of entityGraph.edges) {
        if (
          input.edge_types &&
          input.edge_types.length > 0 &&
          !input.edge_types.includes(edge.relation)
        ) {
          continue;
        }

        let neighborId: string | null = null;
        let direction: "outgoing" | "incoming" = "outgoing";

        if (edge.source === currentId) {
          neighborId = edge.target;
          direction = "outgoing";
        } else if (edge.target === currentId) {
          neighborId = edge.source;
          direction = "incoming";
        }

        if (neighborId && !visited.has(neighborId)) {
          visited.add(neighborId);
          nextFrontier.push(neighborId);
          const node = nodeIdx.get(neighborId);
          neighbors.push({
            id: neighborId,
            label: node?.label,
            label_en: node?.label_en,
            type: node?.type,
            via_relation: edge.relation,
            direction,
            hop,
            petrokgraph_uri: node?.petrokgraph_uri,
            osdu_kind: node?.osdu_kind,
          });
        }
      }
    }

    frontier.length = 0;
    frontier.push(...nextFrontier);
  }

  const origin = nodeIdx.get(input.id)!;

  return JSON.stringify(
    {
      found: true,
      origin: { id: origin.id, label: origin.label, label_en: origin.label_en },
      hops: input.hops,
      edge_types: input.edge_types ?? null,
      neighbors_count: neighbors.length,
      neighbors,
    },
    null,
    2
  );
}
