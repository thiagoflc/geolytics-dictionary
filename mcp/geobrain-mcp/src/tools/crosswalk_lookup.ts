/**
 * crosswalk_lookup — finds equivalent terms across ontology layers.
 *
 * Given any URI (petrokgraph_uri, osdu_kind, geosciml_uri, gso_uri, owl_uri)
 * or a plain entity id, returns matched entities in the graph and their
 * cross-layer URIs. Optionally filters to a specific target layer.
 */

import { z } from "zod";
import { entityGraph, EntityNode } from "../data.js";

export const schema = z.object({
  uri: z
    .string()
    .min(1)
    .describe(
      "URI or entity id to look up. Accepts: petrokgraph_uri, osdu_kind, " +
        "geosciml_uri, gso_uri, owl_uri, or plain entity id (e.g. 'bacia-sedimentar')"
    ),
  target_layer: z
    .enum(["petrokgraph", "osdu", "geosciml", "gso", "owl", "glossary", "extended"])
    .optional()
    .describe("Filter results to equivalents in a specific layer. Omit to return all."),
});

type Input = z.infer<typeof schema>;

const URI_FIELDS: Array<keyof EntityNode> = [
  "petrokgraph_uri",
  "osdu_kind",
  "geosciml_uri",
  "gso_uri",
  "owl_uri",
];

function matchesUri(node: EntityNode, uri: string): boolean {
  const needle = uri.toLowerCase();
  // exact match against any URI field or id
  if ((node.id ?? "").toLowerCase() === needle) return true;
  for (const field of URI_FIELDS) {
    const val = node[field];
    if (typeof val === "string" && val.toLowerCase() === needle) return true;
  }
  return false;
}

function buildCrosswalkEntry(node: EntityNode) {
  return {
    id: node.id,
    label: node.label,
    label_en: node.label_en,
    type: node.type,
    definition: node.definition,
    geocoverage: node.geocoverage,
    uris: {
      petrokgraph: node.petrokgraph_uri ?? null,
      osdu: node.osdu_kind ?? null,
      geosciml: (node as Record<string, unknown>)["geosciml_uri"] ?? null,
      gso: (node as Record<string, unknown>)["gso_uri"] ?? null,
      owl: (node as Record<string, unknown>)["owl_uri"] ?? null,
    },
  };
}

function layerPresent(node: EntityNode, target: string | undefined): boolean {
  if (!target) return true;
  const uris = {
    petrokgraph: node.petrokgraph_uri,
    osdu: node.osdu_kind,
    geosciml: (node as Record<string, unknown>)["geosciml_uri"],
    gso: (node as Record<string, unknown>)["gso_uri"],
    owl: (node as Record<string, unknown>)["owl_uri"],
    glossary: (node as Record<string, unknown>)["glossary_id"],
    extended: (node as Record<string, unknown>)["extended_id"],
  };
  return !!(uris as Record<string, unknown>)[target];
}

export function execute(input: Input): string {
  const matches = entityGraph.nodes.filter((n) => matchesUri(n, input.uri));

  if (matches.length === 0) {
    return JSON.stringify({
      found: false,
      uri: input.uri,
      suggestion:
        "Try an entity id (e.g. 'poco'), a full URI, or an OSDU kind " +
        "(e.g. 'opendes:osdu:master-data--Well:1.0.0').",
    });
  }

  const filtered = input.target_layer
    ? matches.filter((n) => layerPresent(n, input.target_layer))
    : matches;

  return JSON.stringify(
    {
      found: true,
      uri: input.uri,
      target_layer: input.target_layer ?? null,
      matches_count: filtered.length,
      matches: filtered.map(buildCrosswalkEntry),
    },
    null,
    2
  );
}
