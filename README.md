<h1 align="center">Filamentra for Autodesk Fusion</h1>
<p align="center"><strong>Goddess of filaments. Find your shade before you print.</strong><br>Discover real 3D-printing filaments by manufacturer, product line, and color — and bring their appearances into your Fusion designs.</p>

<p align="center"><a href="README.ru.md">Русский</a> · <a href="https://github.com/4FusionLab/Filamentra/issues">Feedback</a> · <a href="https://github.com/4FusionLab">4FusionLab</a></p>

---

## Meet Filamentra

**Filamentra** is an upcoming Autodesk Fusion add-in from **4FusionLab** for browsing filament colors and installing their visual appearances into the current design.

Instead of maintaining a proprietary material-library file, the project aims to provide a searchable catalog of actual 3D-printing filament products. Pick a brand, find a product line and color, and install that appearance only when you need it.

### The intended workflow

1. **Browse** manufacturers, filament families, and color swatches in a dedicated Fusion palette.
2. **Inspect** the product name, color reference, finish, and source information.
3. **Install** an appearance into the active Fusion design without changing any geometry.
4. **Apply** an installed appearance to selected geometry when you choose.
5. **Revisit** installed appearances without creating duplicates.

### What we're planning

| Area | Planned behavior |
| --- | --- |
| Filament catalog | Browse manufacturer → series → color, with search and filters |
| Visual finishes | Approximate matte, glossy, silk, translucent, and composite appearances |
| One-click install | Create an appearance in the active design, not a separate .adsklib |
| Installed inventory | Detect existing catalog appearances and prevent duplicate installs |
| Catalog updates | Distribute versioned data and metadata through GitHub |
| Offline use | Keep a local cache of previously retrieved catalog data |

These are **product goals, not released features**. The exact scope depends on validation against the supported Autodesk Fusion API.

## Project status

🚧 **Planned / pre-development.** No downloadable add-in or verified Fusion implementation is available yet.

The first milestone is a small in-Fusion palette that installs a single test appearance into the current design, followed by verification after saving and reopening the document. The broader catalog comes afterward.

See the [roadmap](docs/ROADMAP.md) for the proposed milestones.

## Appearance, not engineering material

Filamentra is focused on **visual previews during modeling**. It is not intended to provide certified physical properties for stress analysis, manufacturing simulation, or material testing.

Colors and surface finishes are approximations. Monitor calibration, lighting, print orientation, and the actual filament can all affect the look of a printed part. Each catalog entry should link to its source where available.

## Feedback and contributions

Have a filament manufacturer, product line, or color we should consider? [Open an issue](https://github.com/4FusionLab/Filamentra/issues) with the product name and an official reference. See [CONTRIBUTING.md](CONTRIBUTING.md) for data-quality and contribution guidelines.

## A little workshop mythology

**Filamentra**, goddess of filaments, guards an endless collection of colored threads and finishes. She lets makers see the shade of a future print before the printer lays down its first layer.

She joins **[Perfora](https://github.com/4FusionLab/Perfora)**, goddess of holes, **[Selectra](https://github.com/4FusionLab/Selectra)**, goddess of choice, and **[Planara](https://github.com/4FusionLab/Planara)**, goddess of flat worlds, in the original **4FusionLab mythology**.

**Other 4FusionLab tools:** [Ejix — extract solid volumes](https://github.com/4FusionLab/Ejix) · [RuEn — keyboard-layout shortcuts](https://github.com/4FusionLab/RuEn)

---

<sub>Filamentra is an independent 4FusionLab project, not affiliated with or endorsed by Autodesk or filament manufacturers. Autodesk and Fusion are trademarks of Autodesk, Inc. License terms will be published before source distribution or a public release.</sub>
