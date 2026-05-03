# Raw data sources

Unprocessed or lightly-cleaned data sourced from external providers.
Consumed by generators in `scripts/` and by Python loaders in
`python/geobrain/data.py`.

| File | Source | Consumer |
|---|---|---|
| `ontopetro.txt` | OntoPetro vocabulary export. | `scripts/ontopetro-data.js` |

When adding a new raw source:

1. Drop the file here under a self-explanatory name.
2. Note the source URL/provider in the table above.
3. Document the consumer (generator script or loader function).
4. If the file is large or binary, consider Git LFS.
