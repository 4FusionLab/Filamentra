# Multicolor preview renderer — experimental

[Русская версия](MULTICOLOR_RENDERING.ru.md)

Filamentra includes an **offline PNG generator** for manufacturer RGBA display swatches and a **small experimental Fusion API adapter**. The end-to-end Add-In has not yet been tested in Autodesk Fusion and is not ready for release.

## Goals and modes

- Solid: a single verified manufacturer color; use Appearance.color directly (not implemented here).
- Multicolor / co-extrusion-like: generate sharp **UV color bands** from 2+ published swatches.
- Gradient / rainbow: generate smooth **UV gradients** between the published RGBA swatches.

All patterns are **UV-space previews**, not physical simulation of filament extrusion. A printed part's shade distribution depends on print axis, slicer toolpaths, filament feed, spool position, pigment extrusion arrangement, and geometry. Filamentra cannot infer these from swatches alone.

For multi-color data records, the optional "rendering" object controls the default preview. If missing, the generator derives "uv_bands" from color_mode="multicolor" and "uv_gradient" from color_mode="gradient". Orientation and repeat counts can be overridden at runtime by a future UI. Rendering provenance must always be "filamentra_estimate".

## Offline PNG generation

    from filamentra.texture_generator import render_to_cache

    shade = {
        "color_mode": "multicolor",
        "rgba_swatches": ["#3D3D3FFF", "#EC4235FF"]
    }
    texture_path = render_to_cache(shade, "/tmp/filamentra-cache", 512, 512)

The function uses Python standard library only (no PIL, NumPy, or external networking), writes a deterministic RGBA PNG, and caches it by content hash. It preserves all manufacturer swatch channels, including alpha; opacity from a display swatch is **not** equivalent to measured volumetric optical transmission. Gradient interpolation currently mixes channel values in encoded sRGB; it is a preview algorithm, not spectral mixing.

## Fusion API adapter — manual test only

    from filamentra.fusion_appearance import install_preview_appearance

    # Requires an existing adsk.fusion.Design and the generated texture_path.
    appearance = install_preview_appearance(
        design,
        "Filamentra | esun/pla-matte-dual/black-red",
        texture_path,
        roughness=0.86
    )

The adapter calls Design.appearances.add and connects Appearance.colorTexture, then roughness. It intentionally does not assign the Appearance to any geometry, handle persistent IDs, or offer a palette. It targets Fusion July 2026 API+.

Autodesk:
- https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Appearances_add.htm
- https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Appearance_colorTexture.htm
- https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/core_Appearance.htm

## Validation and next implementation steps

Run tests without Fusion:

    python -m unittest discover -s tests -v

Then manually test in Autodesk Fusion on Windows and macOS using a box, a cylinder, and a curved part:

1. Create the appearance without modifying geometry.
2. Verify the UV projection orientation, seams, and repetition for 2-color and 4-color examples.
3. Render in both Design viewport and Render workspace.
4. Save and reopen the design; confirm that embedded texture and roughness persist.
5. Verify actual print samples under controlled lighting before claiming visual calibration.

**Not implemented:** HTML Palette bridge, UV projector controls, per-geometry direction presets, duplicate detection, user-facing rotation, Apply to Selection, catalog Release downloads and verified physical optical simulation. Gradient positioning across layers requires slicer/printer data and is explicitly out of scope for the current texture generator.

Source data and preview hints live in [Filamentra-DataSource](https://github.com/4FusionLab/Filamentra-DataSource). Rendering and Fusion integration live in this repository.
