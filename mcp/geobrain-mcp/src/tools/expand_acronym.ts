/**
 * expand_acronym — expands an O&G sigla/acronym with full disambiguation.
 *
 * Excludes it_generic entries by default unless category="it_generic" is passed.
 */

import { z } from "zod";
import { acronyms, Acronym } from "../data.js";

export const schema = z.object({
  sigla: z.string().min(1).describe("The acronym/sigla to expand (e.g. ANP, BOP, FPSO)"),
  category: z
    .string()
    .optional()
    .describe(
      "Filter by category (standard_body, measurement, general, process, fluid, contract, " +
        "equipment, environmental, it_generic, regulator, lithology, unit, geophysics, " +
        "organization, well_state). Pass 'it_generic' to include generic IT acronyms."
    ),
});

type Input = z.infer<typeof schema>;

export function execute(input: Input): string {
  const needle = input.sigla.toUpperCase().trim();
  const includeItGeneric = input.category === "it_generic";

  let matches: Acronym[] = acronyms.filter((a) => a.sigla.toUpperCase() === needle);

  if (matches.length === 0) {
    return JSON.stringify({
      found: false,
      sigla: input.sigla,
      suggestion: "No exact match. Try a partial search via lookup_term or check spelling.",
    });
  }

  // filter out it_generic unless explicitly requested
  const filtered = includeItGeneric ? matches : matches.filter((a) => !a.it_generic);

  if (input.category && input.category !== "it_generic") {
    const byCat = filtered.filter((a) => a.category === input.category);
    if (byCat.length > 0) {
      matches = byCat;
    } else {
      matches = filtered;
    }
  } else {
    matches = filtered;
  }

  const needsDisambiguation = matches.length > 1;

  return JSON.stringify(
    {
      found: true,
      sigla: input.sigla,
      senses_count: matches.length,
      disambiguation_needed: needsDisambiguation,
      disambiguation_hint: needsDisambiguation
        ? `${matches.length} senses found. Use the 'category' parameter to narrow down: ` +
          matches.map((m) => m.category).join(", ")
        : null,
      senses: matches.map((a) => ({
        id: a.id,
        sigla: a.sigla,
        expansion_pt: a.expansion_pt,
        expansion_en: a.expansion_en,
        category: a.category,
        it_generic: a.it_generic ?? false,
      })),
    },
    null,
    2
  );
}
