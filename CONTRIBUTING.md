# Contributing to Filamentra

[Русская версия](CONTRIBUTING.ru.md)

Thanks for helping improve Filamentra, a planned filament appearance catalog for Autodesk Fusion from [4FusionLab](https://github.com/4FusionLab).

The project is in pre-development. Please open an [issue](https://github.com/4FusionLab/Filamentra/issues) to discuss significant technical changes or new catalog formats before implementing them.

## Proposing a filament

Provide as many of these fields as possible:

- **Manufacturer:** official brand name.
- **Series:** exact product family, such as PLA Matte, PLA+, or PETG.
- **Color name:** official spelling.
- **Product identifier:** SKU, manufacturer code or equivalent where available.
- **Color reference:** manufacturer-published HEX/RGB or another verifiable reference, if available.
- **Finish:** matte, glossy, silk, translucent, composite, or other documented characteristics.
- **Source:** link to an official product or specification page.
- **Date checked:** when the information was verified.

Avoid guessing color values or surface properties. If a value is estimated, label it as an approximation and document why. A product photo is not by itself a reliable colorimetric reference.

## Data principles

1. A catalog ID must remain stable when names or properties change.
2. Do not invent manufacturer/series/color combinations.
3. Do not silently replace source-backed values with guesses.
4. Keep a source trail for externally verifiable data.
5. Do not distribute trademarked images or vendor-provided assets without appropriate rights.
6. Distinguish visual Appearance properties from certified physical material data.

## Development principles

- Keep catalog parsing, validation and synchronization logic testable outside Fusion.
- Use supported Autodesk Fusion API methods for changes to a Design.
- Make install idempotent and apply-to-selection explicit.
- Never change appearances already applied in a user's saved model without an intentional update action.
- Verify Fusion-specific behavior in the real app before claiming support.
- Document limitations and unsuccessful compatibility tests.
- Prefer focused, reviewable changes with a concise explanation.

For current planning and milestones see [docs/ROADMAP.md](docs/ROADMAP.md).

## Reporting issues

For bugs, include Fusion version, operating system, exact steps, actual vs expected behavior and a minimal reproduction where possible. Do not attach private models or proprietary manufacturer files without permission.

## License and code contributions

Filamentra is distributed under the [PolyForm Noncommercial License 1.0.0](LICENSE). Commercial use outside its permitted purposes requires a separate agreement with 4FusionLab; third-party components retain their own licenses. Before submitting substantial code or assets, coordinate their licensing and contribution terms with the maintainers.

Filamentra is independent of Autodesk and filament manufacturers.
