# Eval Harness Report

Generated: 2026-05-01T22:57:33Z

## Summary

| Metric | Vector Only | Graphrag | Graphrag Validator |
| --- | --- | --- | --- |
| Entity Recall (higher=better) | 0.1650 | 0.4978 | 0.4978 |
| Fact Coverage (higher=better) | 0.4189 | 0.3291 | 0.3291 |
| MustNotSay Violations (lower=better) | 0.0278 | 0.0167 | 0.0167 |
| Validation Pass Rate (higher=better) | 1.0000 | 1.0000 | 1.0000 |
| Composite Score (higher=better) | 0.4988 | 0.5861 | 0.5861 |

## Runner Details

### vector_only

- Timestamp: 20260501T225639Z
- Questions evaluated: 30
- Composite score: 0.4988

### graphrag

- Timestamp: 20260501T225642Z
- Questions evaluated: 30
- Composite score: 0.5861

### graphrag_validator

- Timestamp: 20260501T225708Z
- Questions evaluated: 30
- Composite score: 0.5861

## Deltas vs vector_only

| Metric | Graphrag | Graphrag Validator |
| --- | --- | --- |
| Entity Recall (higher=better) | +0.3328 | +0.3328 |
| Fact Coverage (higher=better) | -0.0898 | -0.0898 |
| MustNotSay Violations (lower=better) | -0.0111 | -0.0111 |
| Validation Pass Rate (higher=better) | +0.0000 | +0.0000 |
| Composite Score (higher=better) | +0.0873 | +0.0873 |

## Category Breakdown (graphrag_validator)

| Category | N | Avg Composite |
| --- | --- | --- |
| disambiguation | 4 | 0.7542 |
| geomec | 5 | 0.4317 |
| lookup | 8 | 0.6245 |
| multi-hop | 2 | 0.6967 |
| seismic | 5 | 0.3653 |
| validation | 1 | 0.7083 |
| witsml | 5 | 0.6967 |
