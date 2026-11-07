# Filamentra — Roadmap

[Русская версия](ROADMAP.ru.md)

> Planning document. The milestones below are targets, not promises or completed functionality.

## Guiding principles

- **Visual appearances first.** Filamentra is a catalog of filament appearances, not a mechanical-property database.
- **Install on demand.** The catalog lives outside the Fusion design; only selected appearances are created in the active design.
- **No duplicate installs.** Identify catalog entries by stable IDs, not mutable display names alone.
- **Do not recolor automatically.** Installing an appearance must not change the geometry or apply a finish without an explicit action.
- **Verifiable catalog data.** Record sources and clearly distinguish manufacturer-provided colors from approximations.
- **Test in real Fusion.** Offline unit tests are necessary but insufficient to claim API compatibility.

## Milestone 0 — API feasibility

- Confirm supported Appearance creation and modification methods against current official Fusion API documentation.
- Confirm which attributes and identifiers can persist on an Appearance or in a Design.
- Prototype the HTML Palette ↔ Python bridge and its event lifecycle.
- Record API compatibility findings and limitations.

**Exit criterion:** one well-defined, documented way to create and identify a visual appearance in an active Fusion design.

## Milestone 1 — Palette and Install

- Minimal palette with a small bundled test catalog.
- Install one visual Appearance into the current design without applying it.
- Detect an already installed catalog ID.
- Test save/reopen, multiple install attempts, and document switching.
- Clearly distinguish pending/failed/installed states.

**Fusion acceptance:** appearance creation, persistence, correct color, no duplicates.

## Milestone 2 — Data model and catalog browser

- Versioned JSON schema for manufacturer, series, colors, finish, references, and stable IDs.
- Browse and search catalog entries.
- Local validation for duplicate IDs, invalid colors, inconsistent sources and paths.
- Initially populate a small source-verified selection of real filament products.

**Exit criterion:** catalog validation runs without Autodesk.

## Milestone 3 — Applied appearances

- Explicit Apply to Selection action for supported Fusion geometry.
- Installed-material inventory for the active design.
- Safe removal of unused appearances when Fusion permits.
- Store catalog IDs and content fingerprints for reliable matching.

**Fusion acceptance:** targeted geometry changes only; repeated operations do not generate duplicates.

## Milestone 4 — GitHub distribution and offline cache

- Versioned catalog hosted on GitHub.
- Local cache with offline fallback.
- Check for updates and handle failures without disrupting modeling.
- Avoid silent changes to appearances already used in saved models.

## Milestone 5 — Surface fidelity and wider catalog

- Test finish profiles (matte, glossy, silk, translucent, composite).
- Add textures only after verifying the official Fusion API behavior.
- Expand catalog by manufacturer, series and official color variants.
- Test supported macOS and Windows configurations.

## Not currently in scope

- Writing or modifying Autodesk `.adsklib` files.
- Certified material density, mechanical properties or FEA/CAE datasets.
- Guaranteed colorimetric accuracy against a printed object.
- Inventor runtime, proprietary Autodesk library format reverse engineering, or a separate ADSKLIB builder.
- Silently replacing user-modified appearances.

## Acceptance evidence

For each Fusion-dependent milestone record:
- Fusion version and operating system.
- Exact tested catalog sample.
- What was executed manually versus automatically.
- Actual outcomes, failures and screenshots where useful.
- Remaining compatibility risks.

Do not mark a Fusion milestone as passed without running its tests in Fusion.
