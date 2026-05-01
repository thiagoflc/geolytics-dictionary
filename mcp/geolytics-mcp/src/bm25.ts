/**
 * bm25.ts — minimal BM25 implementation, no external dependencies.
 *
 * Parameters follow the Robertson/Sparck Jones BM25 formulation:
 *   k1 = 1.5, b = 0.75 (standard defaults).
 */

export interface ScoredDoc {
  index: number;
  score: number;
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .normalize("NFD")
    // strip combining diacritics (accents) so "bacia" matches "Bacia"
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .split(" ")
    .filter(Boolean);
}

export class BM25 {
  private readonly k1 = 1.5;
  private readonly b = 0.75;

  private docs: string[][];
  private N: number;
  private avgdl: number;
  private df: Map<string, number>;
  private idf: Map<string, number>;

  constructor(documents: string[]) {
    this.docs = documents.map(tokenize);
    this.N = this.docs.length;

    // average document length
    const totalLen = this.docs.reduce((s, d) => s + d.length, 0);
    this.avgdl = this.N > 0 ? totalLen / this.N : 1;

    // document frequency per term
    this.df = new Map();
    for (const doc of this.docs) {
      const seen = new Set(doc);
      for (const term of seen) {
        this.df.set(term, (this.df.get(term) ?? 0) + 1);
      }
    }

    // IDF — Robertson IDF: log((N - df + 0.5) / (df + 0.5) + 1)
    this.idf = new Map();
    for (const [term, df] of this.df) {
      this.idf.set(
        term,
        Math.log((this.N - df + 0.5) / (df + 0.5) + 1)
      );
    }
  }

  search(query: string, topK = 10): ScoredDoc[] {
    const qTerms = tokenize(query);
    if (qTerms.length === 0) return [];

    const scores: number[] = new Array(this.N).fill(0);

    for (const term of qTerms) {
      const idf = this.idf.get(term) ?? 0;
      if (idf === 0) continue;

      for (let i = 0; i < this.N; i++) {
        const doc = this.docs[i];
        const dl = doc.length;
        const tf = doc.filter((t) => t === term).length;
        if (tf === 0) continue;

        const numerator = tf * (this.k1 + 1);
        const denominator =
          tf + this.k1 * (1 - this.b + this.b * (dl / this.avgdl));
        scores[i] += idf * (numerator / denominator);
      }
    }

    return scores
      .map((score, index) => ({ index, score }))
      .filter((d) => d.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
  }
}
