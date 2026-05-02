/**
 * search_rag — BM25 full-text search over the RAG corpus (ai/rag-corpus.jsonl).
 *
 * No external embedding provider — pure offline BM25.
 * The index is built once on first call and reused.
 */

import { z } from "zod";
import { ragChunks, RagChunk } from "../data.js";
import { BM25 } from "../bm25.js";

export const schema = z.object({
  query: z.string().min(1).describe("Natural-language query to search"),
  k: z
    .number()
    .int()
    .min(1)
    .max(50)
    .optional()
    .default(5)
    .describe("Number of results to return (default 5, max 50)"),
});

type Input = z.infer<typeof schema>;

let _index: BM25 | null = null;

function getIndex(): BM25 {
  if (!_index) {
    const texts = ragChunks.map((c) => c.text ?? "");
    _index = new BM25(texts);
  }
  return _index;
}

export function execute(input: Input): string {
  if (ragChunks.length === 0) {
    return JSON.stringify({
      error: "RAG corpus not loaded",
      detail: "ai/rag-corpus.jsonl is empty or missing.",
    });
  }

  const index = getIndex();
  const hits = index.search(input.query, input.k);

  const results = hits.map((h) => {
    const chunk = ragChunks[h.index] as RagChunk;
    return {
      score: Math.round(h.score * 1000) / 1000,
      id: chunk.id,
      type: chunk.type,
      text: chunk.text,
      metadata: chunk.metadata ?? null,
    };
  });

  return JSON.stringify(
    {
      query: input.query,
      k: input.k,
      total_corpus: ragChunks.length,
      results_count: results.length,
      results,
    },
    null,
    2
  );
}
