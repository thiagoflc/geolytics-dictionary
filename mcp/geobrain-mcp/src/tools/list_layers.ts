/**
 * list_layers — returns all semantic layers from ai/ontology-map.json.
 */

import { z } from "zod";
import { ontologyLayers } from "../data.js";

export const schema = z.object({}).describe("No parameters required");

export function execute(_input: Record<string, never>): string {
  return JSON.stringify(
    {
      count: ontologyLayers.length,
      layers: ontologyLayers.map((l) => ({
        id: l.id,
        name: l.name,
        maintainer: l.maintainer,
        type: l.type,
        description: l.description,
        concepts_count: l.concepts_count,
        language: l.language,
        geolytics_coverage: l.geolytics_coverage,
      })),
    },
    null,
    2
  );
}
