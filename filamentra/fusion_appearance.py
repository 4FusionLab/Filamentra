"""Experimental Autodesk Fusion Appearance adapter (July 2026+).

Installs an appearance into the active *Design*, without applying it to bodies.
All Fusion SDK imports are deferred, so offline tests can inject a mock core.

IMPORTANT: Transmission and haze are not independent exposed Fusion API knobs.
We map the former to a TransparentAppearanceSurface and the latter to an
approximate microfacet-roughness fallback. Both are reported as approximate.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .appearance_mapping import haze_effective_roughness, resolve_catalog_color


@dataclass
class FusionAppearanceReport:
    appearance: Any
    exact: list[str] = field(default_factory=list)
    approximate: dict[str, str] = field(default_factory=dict)
    unavailable: dict[str, str] = field(default_factory=dict)

    @property
    def full_fidelity(self) -> bool:
        return not self.approximate and not self.unavailable


def _core_or_import(core: Any = None) -> Any:
    if core is not None:
        return core
    import adsk.core
    return adsk.core


def _channel_color(hex_rgb: str, alpha: int, core: Any) -> Any:
    if not isinstance(hex_rgb, str) or len(hex_rgb) != 7 or not hex_rgb.startswith("#"):
        raise ValueError("An explicit six-digit HEX color is required")
    try:
        parts = tuple(int(hex_rgb[i:i + 2], 16) for i in (1, 3, 5))
    except ValueError as exc:
        raise ValueError(f"Invalid HEX: {hex_rgb}") from exc
    if not isinstance(alpha, int) or not 0 <= alpha <= 255:
        raise ValueError("opacity must be an 8-bit integer")
    return core.Color.create(*parts, alpha)


def _texture_file(path: str, root: Path | None) -> str:
    if root is None:
        raise FileNotFoundError("texture_root is required to install PBR textures")
    base = root.resolve()
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(base) or not resolved.is_file():
        raise FileNotFoundError(f"Invalid or missing PBR map: {path}")
    return str(resolved)


def _set_property(report: FusionAppearanceReport, design: Any, name: str,
                  prop_id: str, value: float, *, millimeters: bool = False) -> None:
    """Set a supported FloatProperty and verify readback; do not guess units."""
    try:
        prop = report.appearance.appearanceProperties.itemById(prop_id)
        if prop is None or getattr(prop, "isReadOnly", False):
            raise RuntimeError(f"{prop_id} not available or read-only")
        if getattr(prop, "hasMultipleValues", False):
            raise RuntimeError(f"{prop_id} is not a scalar FloatProperty")
        current = prop.value
        if not isinstance(current, (int, float)):
            raise TypeError(f"{prop_id} is not numeric")
        converted = float(value)
        if millimeters:
            units = prop.units
            if not units:
                raise RuntimeError("transparent_distance exposes no known length units")
            converted = float(design.unitsManager.convert(value, "mm", units))
        prop.value = converted
        if not math.isclose(float(prop.value), converted, rel_tol=1e-3, abs_tol=1e-4):
            raise RuntimeError("property did not retain the written value")
        report.exact.append(name)
    except Exception as exc:
        report.unavailable[name] = f"{prop_id}: {exc}"


def install_resolved_appearance(
    design: Any, name: str, hex_rgb: str, resolved: dict,
    *, texture_root: str | Path | None = None, core: Any = None,
) -> FusionAppearanceReport:
    """Create one color-specific Appearance with a transparent fidelity report.

    This does not do an actual Fusion test: in-Fusion save/reopen and render
    verification remain mandatory before claiming pixel-equivalent fidelity.
    """
    core = _core_or_import(core)
    if not name or not name.strip():
        raise ValueError("Appearance name must be nonempty")
    surface = resolved.get("surface_type", "opaque")
    if surface not in ("opaque", "metallic", "transparent"):
        raise ValueError(f"Unknown surface_type: {surface}")
    roughness = float(resolved.get("roughness", 0.4))
    haze = float(resolved.get("haze", 0))
    transmission = float(resolved.get("transmission", 0))
    if not all(math.isfinite(v) and 0 <= v <= 1 for v in (roughness, haze, transmission)):
        raise ValueError("roughness, haze and transmission must be finite values in 0..1")
    if transmission > 0 and surface != "transparent":
        raise ValueError("Positive transmission requires a transparent surface")
    alpha = int(resolved.get("opacity", 255))
    tint = _channel_color(hex_rgb, 255 if surface == "transparent" else alpha, core)
    surface_enum = {
        "opaque": core.AppearanceSurfaceTypes.OpaqueAppearanceSurface,
        "metallic": core.AppearanceSurfaceTypes.MetallicAppearanceSurface,
        "transparent": core.AppearanceSurfaceTypes.TransparentAppearanceSurface,
    }[surface]
    appearance = design.appearances.add(name, surface_enum)
    if appearance is None:
        raise RuntimeError("Fusion did not create a Design Appearance")
    report = FusionAppearanceReport(appearance=appearance)
    base = Path(texture_root) if texture_root is not None else None

    try:
        appearance.color = tint
        report.exact.extend(["surface_type", "color"])
        if surface != "transparent":
            report.exact.append("opacity")
        else:
            report.approximate["transmission"] = (
                "Fusion transparent-volume surface; API has no independently writable "
                "PBR light-transmission fraction (stored value is not applied numerically)."
            )
            if alpha != 255:
                report.unavailable["opacity"] = (
                    "Separate alpha on a transparent volume cannot be assumed equivalent "
                    "to optical transmission; alpha intentionally forced to 255."
                )

        if surface == "transparent" and "ior" in resolved:
            _set_property(report, design, "ior", "transparent_ior", float(resolved["ior"]))
        if surface == "transparent" and "attenuation_distance_mm" in resolved:
            _set_property(report, design, "attenuation_distance_mm",
                          "transparent_distance", float(resolved["attenuation_distance_mm"]),
                          millimeters=True)

        textures = resolved.get("textures") or {}
        for field_name, slot in (("base_color", "colorTexture"), ("normal_gl", "normalTexture")):
            if field_name in textures:
                try:
                    filename = _texture_file(textures[field_name], base)
                    setattr(appearance, slot, filename)
                    if not getattr(appearance, slot):
                        raise RuntimeError(f"Fusion rejected {slot}")
                    report.exact.append("textures." + field_name)
                except Exception as exc:
                    report.unavailable["textures." + field_name] = str(exc)

        if textures.get("roughness") and haze <= 0:
            try:
                filename = _texture_file(textures["roughness"], base)
                appearance.roughnessTexture = filename
                if not appearance.roughnessTexture:
                    raise RuntimeError("Fusion rejected roughnessTexture")
                report.exact.append("textures.roughness")
            except Exception as exc:
                report.unavailable["textures.roughness"] = str(exc)
        elif textures.get("roughness") and haze > 0:
            report.unavailable["textures.roughness"] = (
                "Skipped original roughness map: direct volumetric haze is unavailable; "
                "the scalar roughness fallback must control light diffusion."
            )

        effective = haze_effective_roughness(haze, roughness) if haze > 0 else roughness
        appearance.roughness = effective   # must be set *after* roughnessTexture
        if not math.isclose(float(appearance.roughness), effective, abs_tol=1e-3):
            raise RuntimeError("Fusion did not retain roughness")
        report.exact.append("roughness" if haze == 0 else "roughness_fallback")
        if haze > 0:
            report.approximate["haze"] = (
                f"No direct Fusion haze/volume-scattering property; using roughness "
                f"{effective:.3f} instead of {roughness:.3f}. "
                "This also changes highlights and cannot match Pages exactly."
            )
        if surface != "transparent" and "haze" in resolved and haze > 0:
            report.unavailable["haze_surface"] = "Non-transparent surface cannot transmit blurred imagery"
        return report
    except Exception:
        # Do not leave a partially created appearance on a fatal failure.
        try:
            appearance.deleteMe()
        except Exception:
            pass
        raise


def install_catalog_color(design: Any, line: dict, color: dict, presets: dict,
                          *, texture_root: str | Path | None = None,
                          core: Any = None) -> FusionAppearanceReport:
    """Install one manufacturer/line/color variant, without changing geometry."""
    resolved, hex_rgb, neutral_clear = resolve_catalog_color(line, color, presets)
    name = f"Filamentra | {line.get('brand', '?')} | {line['name']} | {color['name']}"
    report = install_resolved_appearance(
        design, name, hex_rgb, resolved, texture_root=texture_root, core=core
    )
    if neutral_clear:
        report.approximate["color"] = (
            "Manufacturer Clear uses a fully transparent RGBA screen swatch, "
            "not a measured dye tint; used neutral preview-only appearance color."
        )
    return report
