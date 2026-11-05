"""Renderer-neutral appearance resolution and visual-fidelity bookkeeping.

The catalog schema stays v1. Haze is a qualitative 0..1 Filamentra estimate:
it is *not* opacity, microfacet roughness, or a measured scattering coefficient.
No Autodesk imports are used in this module.
"""
from __future__ import annotations

import re

_RGB = re.compile(r"^#[0-9A-Fa-f]{6}$")
_RGBA_CLEAR = re.compile(r"^#[0-9A-Fa-f]{6}00$")


def resolve_appearance(preset: dict, line: dict | None = None,
                       color: dict | None = None) -> dict:
    """Inheritance: preset → line → color, with per-texture key overrides."""
    resolved = dict(preset or {})
    for override in (line or {}, color or {}):
        for key, value in override.items():
            if key == "textures":
                resolved[key] = {**resolved.get("textures", {}), **value}
            else:
                resolved[key] = value
    for field in ("transmission", "haze", "roughness"):
        if field in resolved:
            value = resolved[field]
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0 <= value <= 1:
                raise ValueError(f"{field} must be within 0..1")
    if resolved.get("transmission", 0) > 0 and resolved.get("surface_type") != "transparent":
        raise ValueError("Transmissive material must have transparent surface_type")
    return resolved


def preview_hex(color: dict) -> tuple[str, bool]:
    """Return a color and whether it is a *render-only* untinted clear default."""
    measured = (color.get("measured_sample") or {}).get("hex")
    value = measured if isinstance(measured, str) and _RGB.fullmatch(measured) else color.get("hex")
    if isinstance(value, str) and _RGB.fullmatch(value):
        return value.upper(), False
    swatches = color.get("rgba_swatches") or []
    if color.get("color_mode") in ("multicolor", "gradient") or len(swatches) != 1:
        raise ValueError("A single documented tint is required; no invented multicolor")
    swatch = swatches[0]
    if not isinstance(swatch, str):
        raise ValueError("Invalid swatch")
    if re.fullmatch(r"#[0-9A-Fa-f]{6}FF", swatch, flags=re.IGNORECASE):
        return swatch[:7].upper(), False
    if _RGBA_CLEAR.fullmatch(swatch):
        # Visual convention only. Never persist as manufacturer's HEX.
        return "#F6F9F7", True
    raise ValueError("No reliable numeric tint for this color")


def haze_effective_roughness(haze: float, surface_roughness: float) -> float:
    """Match Pages visual fallback, not a physical volumetric haze mapping."""
    if not 0 <= haze <= 1 or not 0 <= surface_roughness <= 1:
        raise ValueError("haze and roughness must be 0..1")
    return max(surface_roughness, 0.16 + 0.56 * haze)


def resolve_catalog_color(line: dict, color: dict, presets: dict) -> tuple[dict, str, bool]:
    preset_id = line.get("appearance_preset")
    if preset_id not in presets:
        raise ValueError(f"Unresolved appearance preset: {preset_id}")
    preset = presets[preset_id].get("appearance", {})
    appearance = resolve_appearance(preset, line.get("appearance"), color.get("appearance"))
    hex_color, render_only = preview_hex(color)
    if render_only and not (appearance.get("surface_type") == "transparent"
                            and appearance.get("transmission", 0) > 0):
        raise ValueError("A transparent-clear swatch requires a transmissive appearance")
    return appearance, hex_color, render_only
