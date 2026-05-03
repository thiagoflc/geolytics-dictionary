# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Commits follow [Conventional Commits](https://www.conventionalcommits.org/) — prefixes:

- `feat:` user-facing feature
- `fix:` bug fix
- `docs:` documentation only
- `chore:` maintenance, no behavior change
- `refactor:` code restructure, no behavior change
- `test:` tests only
- `ci:` CI/CD only
- `perf:` performance improvement

Breaking changes are flagged with `!` after the type (e.g. `feat!:`) or a
`BREAKING CHANGE:` footer.

---

## [Unreleased]

### Added
- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`.
- `.editorconfig`, `.gitattributes`, `.prettierrc.json`, `.pre-commit-config.yaml`.
- `.github/CODEOWNERS`, `.github/ISSUE_TEMPLATE/` (bug, feature, config).
- Modular CI workflows split from monolithic `ci.yml`.
- `[tool.ruff]`, `[tool.pytest.ini_options]`, `[project.optional-dependencies.scripts|dev]` in `python/pyproject.toml`.

### Changed
- Reorganized `scripts/` — one-shot dated migrations moved to `scripts/migrations/<date>/`.
- Consolidated Python deps: `scripts/requirements.txt` removed in favor of `python/pyproject.toml [project.optional-dependencies.scripts]`.
- Moved `ontopetro.txt` to `data/raw/`.
- Centralized Python tests in `python/tests/`.

### Removed
- `scripts/requirements.txt` (consolidated).
- 4 stale local branches.

---

## How to release

1. Bump version in `python/geobrain/_version.py`.
2. Move `## [Unreleased]` content into a new `## [x.y.z] — YYYY-MM-DD` section.
3. Create a new empty `## [Unreleased]` block on top.
4. Tag: `git tag -s vx.y.z -m "vx.y.z"` and push.
5. The `release.yml` workflow publishes to PyPI.
