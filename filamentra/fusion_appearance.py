"""Experimental adapter: requires Autodesk Fusion July 2026 API or newer.

This is not a complete Add-In. It does not apply an Appearance to model geometry.
"""

from pathlib import Path


def install_preview_appearance(design, name: str, texture_file: str | Path,
                               roughness: float = 0.4):
    import adsk.core  # Only available inside Autodesk Fusion.

    if not name or not str(name).strip():
        raise ValueError("A nonempty Appearance name is required")
    if not 0 <= roughness <= 1:
        raise ValueError("Roughness must be within 0..1")
    path = Path(texture_file).resolve()
    if not path.is_file() or path.suffix.lower() != ".png":
        raise FileNotFoundError(str(path))
    appearance = design.appearances.add(
        name, adsk.core.AppearanceSurfaceTypes.OpaqueAppearanceSurface)
    if appearance is None:
        raise RuntimeError("Could not create Appearance in the Design")
    try:
        appearance.colorTexture = str(path)
        if not appearance.colorTexture:
            raise RuntimeError("Fusion did not connect colorTexture")
        appearance.roughness = float(roughness)
        return appearance
    except Exception:
        try:
            appearance.deleteMe()
        except Exception:
            pass
        raise
