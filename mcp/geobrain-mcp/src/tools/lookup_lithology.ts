/**
 * lookup_lithology — look up CGI Simple Lithology concepts.
 *
 * Search the 437-concept CGI vocabulary by label (PT or EN), parent class,
 * or OSDU LithologyType equivalent. Returns matching concepts with definitions
 * and cross-references.
 */
import { z } from "zod";
import { cgiLithology, CgiLithologyConcept } from "../data.js";

export const schema = z.object({
  query: z.string().min(1).describe(
    "Search term — matches label_en, label_pt, or id. E.g. 'limestone', 'calcário', 'sandstone'"
  ),
  parent: z.string().optional().describe(
    "Filter by parent class (e.g. 'sedimentary_material', 'igneous_material')"
  ),
  max_results: z.number().int().min(1).max(50).default(10),
});

type Input = z.infer<typeof schema>;

export function handler(input: Input): object {
  const q = input.query.toLowerCase();
  let results: CgiLithologyConcept[] = cgiLithology.filter(concept => {
    const matchesQuery =
      concept.id.toLowerCase().includes(q) ||
      (concept.label_en ?? "").toLowerCase().includes(q) ||
      (concept.label_pt ?? "").toLowerCase().includes(q);
    const matchesParent = !input.parent || (concept.parents ?? []).includes(input.parent);
    return matchesQuery && matchesParent;
  });

  if (results.length === 0) {
    return { found: false, message: `No CGI lithology concepts matching '${input.query}'`, results: [] };
  }

  results = results.slice(0, input.max_results);
  return {
    found: true,
    total: results.length,
    source: "CGI Simple Lithology OWL Vocabulary (IUGS/CGI 2021)",
    results: results.map(c => ({
      id: c.id,
      label_en: c.label_en,
      label_pt: c.label_pt ?? null,
      definition: c.definition_en ?? null,
      parents: c.parents ?? [],
      uri: c.uri ?? null,
    })),
  };
}

export function execute(input: Input): string {
  return JSON.stringify(handler(input), null, 2);
}
