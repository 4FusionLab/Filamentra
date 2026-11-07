# Filamentra development

[Русская версия](AGENTS.ru.md)

Filamentra is a planned Fusion add-in for finding filaments and installing visual Appearances. Working Python modules exist, but a complete installable add-in does not yet exist.

## Shared 4FusionLab rules

- Shared standards: https://github.com/4FusionLab/.github/blob/main/AGENTS.md; shared CI model: https://github.com/4FusionLab/.github/blob/main/RELEASE_PLATFORM.md.
- Communicate and make plans in Russian; use English for code and Fusion UI. Retain separate README.md and README.ru.md.
- Inspect current files and Git status before changes. Use Conventional Commits; a PR with passing checks is preferred, and direct push to main is allowed.
- Do not change Fusion manifest UUIDs, command IDs, OS support or package format without a migration plan. Do not commit secrets, tokens or personal CAD files.
- Where runtime exists, a push or merge to main creates a release only for paths in .github/release-paths.txt after successful CI. Use GitVersion.Tool 6.8.2, an automatically created immutable tag and GitHub Release; do not create tags manually.
- Docs, README, tests, AGENTS.md or CI changes must not independently publish a release. Pin shared Actions only to a specific commit SHA.
- Unit tests and ZIPs do not replace native Autodesk Fusion validation. Preserve existing limitations and compatibility evidence.

## Implementation rules

- Verify implemented capabilities against README.md, README.ru.md and docs/ROADMAP.md. Do not present planned UI, catalog downloads or installation in Fusion as completed functionality.
- Main modules: filamentra/appearance_mapping.py, filamentra/fusion_appearance.py and filamentra/texture_generator.py. Preserve determinism, provenance and the boundaries of the actual Fusion API.
- Filamentra-DataSource data are visual approximations, not certified mechanical or optical parameters. Do not invent manufacturers, SKUs or shades.
- The release currently distributes a source ZIP of Python modules and SHA-256, not a finished Fusion installer. Changing the package format requires separate review.
- Run `python -m unittest discover -s tests -v`, `python scripts/build_release.py --version X.Y.Z` and checksum verification. Claim native Fusion behavior only after a separate CAD test.
