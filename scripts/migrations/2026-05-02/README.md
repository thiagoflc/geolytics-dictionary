# Migrations — 2026-05-02

One-shot data-governance scripts applied on **2026-05-02**. They are kept
in the repo for historical reference and reproducibility, but **should not
be re-run** against current data — they were idempotent at the time of
application but assume the schema state of that date.

## Scripts

| Script | Purpose | Status |
|---|---|---|
| `add-frente-f-entities.py` | Added 8 low-confidence skeleton entities for the "Frente F" governance review. | ✅ Applied |
| `add-lab-tests.py` | Added 7 lab-test entities (geomechanical/petrophysical assays) to the corporate module. | ✅ Applied |
| `add-labtest-shacl.py` | Added SHACL shapes asserting lab-test provenance invariants. | ✅ Applied |
| `apply-frente-f-team-response.py` | Applied team responses to "Frente F" — split decisions, vocabulary canonicalization. | ✅ Applied |
| `apply-vocabulary-canonicalization.py` | Canonicalized relation vocabulary per data-governance approval. | ✅ Applied |
| `apply-vocabulary-decisions.py` | Applied 10 vocabulary decisions from the data-governance team. | ✅ Applied |
| `backfill-labtest-provenance.py` | Backfilled `provenance.labTest` field on geomechanical property entities. | ✅ Applied |
| `resolve-formula-variable-overlap.py` | Resolved overlap between GEOMEC036 formula variables and GEOMEC038/039 entities. | ✅ Applied |

## Re-running for audit

If you need to verify what these scripts did, run with `--dry-run`:

```bash
python scripts/migrations/2026-05-02/<script>.py --dry-run
```

`--dry-run` prints the diff that *would* be applied without writing
changes to disk. Compare against the commit history of `data/` from
2026-05-02 to confirm reproducibility.

## Adding a new migration

1. Create `scripts/migrations/<YYYY-MM-DD>/`.
2. Add the script(s) plus a README following this template.
3. Reference the migration in `CHANGELOG.md` under the matching release.
