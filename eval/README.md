# Eval Harness — geolytics-dictionary

Offline evaluation harness for the geolytics-dictionary knowledge-graph RAG system.
Used to measure and compare retrieval quality across runner configurations.

---

## Design

### Golden Set (`eval/golden-set.jsonl`)

105 manually curated question-answer pairs covering seven categories:

| Category | Description |
| --- | --- |
| lookup | Direct term definition retrieval |
| multi-hop | Questions requiring two or more entity joins |
| validation | Claims that must be rejected by the semantic validator |
| disambiguation | Pairs of easily confused concepts |
| geomec | Geomechanics and rock-mechanics terms |
| seismic | Seismic acquisition and processing terminology |
| witsml | WITSML / drilling data schema questions |

Each line follows the schema:

```json
{
  "id": "Q001",
  "question_pt": "...",
  "expected_facts": ["..."],
  "expected_entities": ["..."],
  "must_not_say": ["..."],
  "category": "lookup",
  "difficulty": "easy|medium|hard",
  "trap_type": "null|...",
  "source_layer": "layer1..7"
}
```

### Runners (`eval/runners/`)

| Runner | Description |
| --- | --- |
| `vector_only` | BM25 over `ai/rag-corpus.jsonl` (1952 passages). No graph. |
| `graphrag` | BM25 seed-entity detection, then 2-hop NetworkX expansion over `data/entity-graph.json`. |
| `graphrag_validator` | Same as `graphrag` plus sentence-level semantic validation via `node scripts/validate-cli.js`. Flagged sentences are removed. |

### Metrics (`eval/metrics.py`)

| Metric | Description | Weight |
| --- | --- | --- |
| `entity_recall` | Fraction of expected entities cited | 0.35 |
| `fact_coverage` | Fraction of expected fact tokens in answer | 0.35 |
| `must_not_say_violations` | Rate of forbidden phrases present (lower is better) | 0.20 |
| `validation_pass_rate` | 1 - (violations / 10), capped at 0 | 0.10 |
| `composite_score` | Weighted combination of above | — |

Composite formula:

```
composite = 0.35 * entity_recall
           + 0.35 * fact_coverage
           + 0.20 * (1 - must_not_say_violations)
           + 0.10 * validation_pass_rate
```

---

## Running the Harness

Install the only non-stdlib dependency:

```bash
pip install --user rank-bm25
```

Run all three runners (from the project root):

```bash
python3 eval/run.py --runner vector_only --offline --limit 30
python3 eval/run.py --runner graphrag --offline --limit 30
python3 eval/run.py --runner graphrag_validator --offline --limit 30
python3 eval/report.py
```

Remove `--limit` to evaluate the full 105-question golden set.

Result files land in `eval/results/<runner>-<timestamp>.json`.
The report is written to `eval/results/report.md`.

---

## CI Baseline

`eval/baseline.json` contains the most recent `graphrag_validator` full-run
result and is committed to the repository.

CI regression check (add to your CI script):

```bash
python3 eval/run.py --runner graphrag_validator --offline
python3 - <<'EOF'
import json, sys, pathlib
baseline = json.loads(pathlib.Path("eval/baseline.json").read_text())
latest_f = sorted(pathlib.Path("eval/results").glob("graphrag_validator-*.json"))[-1]
latest = json.loads(latest_f.read_text())
base_cs = baseline["scores"]["composite_score"]
curr_cs = latest["scores"]["composite_score"]
threshold = 0.03
if curr_cs < base_cs - threshold:
    print(f"REGRESSION: composite {curr_cs:.4f} < baseline {base_cs:.4f} - {threshold}")
    sys.exit(1)
print(f"OK: composite {curr_cs:.4f} (baseline {base_cs:.4f})")
EOF
```

---

## Adding Questions

Append a new JSON line to `eval/golden-set.jsonl` following the schema above.
Guidelines:

1. Use real Brazilian petroleum regulation terminology.
2. `expected_entities` should match IDs in `data/entity-graph.json`.
3. `expected_facts` should be key tokens present in `ai/rag-corpus.jsonl`.
4. Fill `must_not_say` with common misconceptions or hallucination attractors.
5. Use `trap_type` to label the kind of confusion the question tests.

---

## Adding Runners

1. Create `eval/runners/<name>.py` with a `run(question: str, **kwargs) -> Answer` function.
2. `Answer` is imported from `eval.runners.vector_only`.
3. Keep runners under 150 lines; delegate shared logic to helpers.
4. Add the runner name to `VALID_RUNNERS` in `eval/run.py`.

---

## Interpretation Guide

- **entity_recall > 0.6** indicates the runner is finding the right concept space.
- **fact_coverage > 0.5** indicates key definitional tokens are present in the answer.
- **must_not_say_violations < 0.1** indicates the runner avoids known misconceptions.
- **composite_score > 0.55** is the target threshold for production readiness.

---

## Thesis Citation

This harness was developed as part of:

> Lopes, T. F. (2026). *Geolytics Dictionary: A Knowledge-Graph-Augmented
> Retrieval System for Brazilian Petroleum Regulation Terminology*.
> Master's thesis, Universidade X.

The eval design follows the offline-first principle described in Chapter 4
(Evaluation Methodology), where reproducibility without external API calls
is a core requirement.
