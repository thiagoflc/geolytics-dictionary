/**
 * lookup_term — searches glossary.json, extended-terms.json and ontopetro classes.
 *
 * fuzzy=true also matches tokens inside definition and synonyms, not just the term name.
 */

import { z } from "zod";
import {
  glossaryTerms,
  extendedTerms,
  ontopetroClasses,
  GlossaryTerm,
  OntopetroClass,
} from "../data.js";

export const schema = z.object({
  term: z.string().min(1).describe("Term to search (PT or EN)"),
  fuzzy: z
    .boolean()
    .optional()
    .default(false)
    .describe("If true, also search inside definitions and synonyms"),
});

type Input = z.infer<typeof schema>;

function normalize(s: string): string {
  return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim();
}

function matchesTerm(term: GlossaryTerm, needle: string, fuzzy: boolean): boolean {
  const n = normalize(needle);

  if (normalize(term.termo ?? "").includes(n)) return true;
  if (normalize(term.termo_en ?? "").includes(n)) return true;
  if (normalize(term.id ?? "").includes(n)) return true;

  if (fuzzy) {
    const synonymsPt = (term.synonyms_pt ?? []).map(normalize);
    const synonymsEn = (term.synonyms_en ?? []).map(normalize);
    if (synonymsPt.some((s) => s.includes(n))) return true;
    if (synonymsEn.some((s) => s.includes(n))) return true;
    if (normalize(term.definicao ?? "").includes(n)) return true;
  }

  return false;
}

function matchesOntopetro(cls: OntopetroClass, needle: string, fuzzy: boolean): boolean {
  const n = normalize(needle);
  if (normalize(cls.name ?? "").includes(n)) return true;
  if (normalize(cls.name_en ?? "").includes(n)) return true;
  if (normalize(cls.id ?? "").includes(n)) return true;
  if (fuzzy && normalize(cls.description ?? "").includes(n)) return true;
  return false;
}

export function execute(input: Input): string {
  const glossaryHits = glossaryTerms.filter((t) => matchesTerm(t, input.term, input.fuzzy));
  const extendedHits = extendedTerms.filter((t) => matchesTerm(t, input.term, input.fuzzy));
  const ontopetroHits = ontopetroClasses.filter((c) =>
    matchesOntopetro(c, input.term, input.fuzzy)
  );

  if (glossaryHits.length === 0 && extendedHits.length === 0 && ontopetroHits.length === 0) {
    return JSON.stringify({
      found: false,
      query: input.term,
      suggestion: "Try fuzzy=true or expand_acronym if searching a sigla.",
    });
  }

  const results = {
    found: true,
    query: input.term,
    fuzzy: input.fuzzy,
    glossary: glossaryHits.map((t) => ({
      source: "glossary",
      id: t.id,
      termo: t.termo,
      termo_en: t.termo_en,
      categoria: t.categoria,
      definicao: t.definicao,
      legal_source: t.legal_source ?? t.fonte,
      petrokgraph_uri: t.petrokgraph_uri,
      osdu_kind: t.osdu_kind,
      geocoverage: t.geocoverage,
      synonyms_pt: t.synonyms_pt,
      synonyms_en: t.synonyms_en,
      examples: t.examples,
      apareceEm: t.apareceEm,
    })),
    extended: extendedHits.map((t) => ({
      source: "extended-terms",
      id: t.id,
      termo: t.termo,
      termo_en: t.termo_en,
      categoria: t.categoria,
      definicao: t.definicao,
      legal_source: t.legal_source,
      petrokgraph_uri: t.petrokgraph_uri,
      osdu_kind: t.osdu_kind,
      geocoverage: t.geocoverage,
      synonyms_pt: t.synonyms_pt,
      synonyms_en: t.synonyms_en,
      examples: t.examples,
    })),
    ontopetro: ontopetroHits.map((c) => ({
      source: "ontopetro",
      id: c.id,
      name: c.name,
      name_en: c.name_en,
      superclass: c.superclass,
      description: c.description,
      domain: c.domain,
      sources: c.sources,
      entity_graph_id: c.entity_graph_id,
    })),
  };

  return JSON.stringify(results, null, 2);
}
