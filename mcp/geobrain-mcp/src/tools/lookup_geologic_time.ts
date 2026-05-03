/**
 * lookup_geologic_time — look up ICS 2023 geologic time scale units.
 *
 * Search the 52-unit ICS 2023 time scale by label (PT or EN), rank
 * (eon/era/period/epoch/age), or time range. Returns age bounds in Ma and
 * Brazil-specific stratigraphic notes where available.
 */
import { z } from "zod";
import { cgiGeologicTime, CgiGeologicTimeUnit } from "../data.js";

export const schema = z.object({
  query: z.string().optional().describe(
    "Label to search (PT or EN). E.g. 'cretáceo', 'Cretaceous', 'aptiano'"
  ),
  rank: z.enum(["eon","era","period","epoch","age"]).optional().describe(
    "Filter by rank in the time scale hierarchy"
  ),
  max_results: z.number().int().min(1).max(30).default(10),
});

type Input = z.infer<typeof schema>;

export function handler(input: Input) {
  let units = [...cgiGeologicTime];

  if (input.query) {
    const q = input.query.toLowerCase();
    units = units.filter(u =>
      u.id.toLowerCase().includes(q) ||
      u.label_en.toLowerCase().includes(q) ||
      (u.label_pt ?? "").toLowerCase().includes(q)
    );
  }

  if (input.rank) {
    units = units.filter(u => u.rank === input.rank);
  }

  units = units.slice(0, input.max_results);

  if (units.length === 0) {
    return { found: false, message: "No matching time scale units", results: [] };
  }

  return {
    found: true,
    total: units.length,
    source: "ICS International Chronostratigraphic Chart 2023",
    results: units.map((u: CgiGeologicTimeUnit) => ({
      id: u.id,
      rank: u.rank,
      label_en: u.label_en,
      label_pt: u.label_pt ?? null,
      start_ma: u.start_ma ?? null,
      end_ma: u.end_ma ?? null,
      duration_ma: (u.start_ma != null && u.end_ma != null)
        ? Math.round((u.start_ma - u.end_ma) * 10) / 10
        : null,
      parent: u.parent ?? null,
      brazil_notes: u.brazil_notes ?? null,
      uri: u.uri ?? null,
    })),
  };
}

export function execute(input: Input): string {
  return JSON.stringify(handler(input), null, 2);
}
