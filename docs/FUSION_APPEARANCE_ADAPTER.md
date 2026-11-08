# Fusion Appearance adapter — transmission and haze

[Русская версия](FUSION_APPEARANCE_ADAPTER.ru.md)

Status: experimental SDK adapter, with offline mock tests only. The package
does NOT contain a complete Palette or installer UI. No in-Fusion render, save
or reopen test has been executed.

## Mapping from Filamentra v1

Data follows the same inheritance as the source catalog: preset -> line -> color.

| Field | Autodesk Fusion mapping | Fidelity |
| --- | --- | --- |
| HEX/opaque alpha | Appearance.color = Color.create(...) | Direct |
| surface_type | AppearanceSurfaceTypes.* + Appearances.add | Direct |
| roughness | Appearance.roughness | Direct when haze = 0 |
| normal_gl | Appearance.normalTexture | Direct if local asset exists |
| textures.roughness | Appearance.roughnessTexture | Direct when haze = 0 |
| ior | appearanceProperties.itemById('transparent_ior').value | Direct with runtime verification |
| attenuation_distance_mm | itemById('transparent_distance').value | Direct only with known units and readback |
| transmission | TransparentAppearanceSurface instead of scalar | Approximate; numeric strength not applied |
| haze | Higher surface roughness | Approximate; changes reflections and is not volume scattering |

There is NO documented independent Fusion API property for haze or for
the exact numeric light-transmission fraction. The adapter does NOT convert
either to alpha. Unsupported mappings, absent PBR assets, read-only properties,
unrecognized units and fidelity reductions are documented in the returned
FusionAppearanceReport (exact, approximate, unavailable).

It is safer to omit the original roughness texture for hazy materials than to
let that map silently cancel the haze-induced scalar roughness.

The adapter converts attenuation distance using the units returned by
FloatProperty.units; if units cannot be established, it reports the property
as unavailable without guessing. A neutral Clear preview color is a renderer
convention, NOT a claim about a manufacturer's measured HEX.

## Example inside Autodesk Fusion (July 2026+)

    from filamentra.fusion_appearance import install_catalog_color

    report = install_catalog_color(
        design, line, color, presets_by_id,
        texture_root="/path/to/local/extracted/catalog",
    )
    print(report.exact)
    print(report.approximate)
    print(report.unavailable)

This installs an Appearance in the Design. It does not apply the appearance
to geometry and does not change the selected bodies.

Official references:
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Appearance.htm
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_AppearanceSurfaceTypes.htm
https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_FloatProperty_units.htm

## Real-Fusion acceptance is not complete

Run on a supported macOS/Windows Fusion build. Create PLA Translucent,
PETG Translucent and PETG Clear in the same Design. Inspect IOR, attenuation
units and roughness. Render at 0.8, 2 and 10 mm sample wall thickness, with
the fixed 4FusionLab logo behind them. Verify save/reopen and report
differences between Design viewport and Render workspace. Do not claim full
optical equivalence to Filamentra Pages without this verification.
