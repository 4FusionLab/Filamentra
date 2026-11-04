"""Procedural UV textures for filament previews; stdlib only, not slicer-accurate."""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import tempfile
import zlib
from pathlib import Path

GENERATOR_VERSION = 1
MAX_DIMENSION = 2048


def parse_rgba(code: str) -> tuple[int, int, int, int]:
    if not isinstance(code, str) or len(code) != 9 or not code.startswith("#"):
        raise ValueError("Expected #RRGGBBAA")
    try:
        return tuple(int(code[i:i + 2], 16) for i in (1, 3, 5, 7))
    except ValueError as exc:
        raise ValueError("Invalid RGBA hex digits") from exc


def options_for_color(color: dict) -> dict:
    mode = color.get("color_mode")
    if mode not in ("gradient", "multicolor"):
        raise ValueError("Procedural texture needs gradient or multicolor mode")
    swatches = color.get("rgba_swatches", [])
    if not isinstance(swatches, list) or len(swatches) < 2:
        raise ValueError("At least two RGBA swatches required")
    for code in swatches:
        parse_rgba(code)
    cfg = color.get("rendering") or {}
    if cfg.get("strategy", "procedural_texture") != "procedural_texture":
        raise ValueError("Unsupported rendering strategy")
    expected = "uv_gradient" if mode == "gradient" else "uv_bands"
    if cfg.get("pattern", expected) != expected:
        raise ValueError("Rendering pattern must match the color mode")
    angle = float(cfg.get("orientation_degrees", 0))
    repeats = cfg.get("repeats", 1)
    if not math.isfinite(angle) or not 0 <= angle <= 360:
        raise ValueError("Orientation must be 0 to 360 degrees")
    if type(repeats) is not int or not 1 <= repeats <= 16:
        raise ValueError("Repeats must be integer 1..16")
    return {"pattern": expected, "orientation_degrees": angle, "repeats": repeats}


def _chunk(tag: bytes, data: bytes) -> bytes:
    payload = tag + data
    return (struct.pack(">I", len(data)) + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF))


def _sample(t: float, colors: list[tuple[int, int, int, int]], pattern: str):
    if pattern == "uv_bands":
        return colors[min(int(t * len(colors)), len(colors) - 1)]
    step = t * (len(colors) - 1)
    i = min(int(step), len(colors) - 1)
    j = min(i + 1, len(colors) - 1)
    weight = step - i
    return tuple(round(a * (1 - weight) + b * weight)
                 for a, b in zip(colors[i], colors[j]))


def texture_png(color: dict, width: int = 512, height: int = 512,
                *, orientation_degrees: float | None = None,
                repeats: int | None = None) -> bytes:
    """Create deterministic 8-bit RGBA PNG from official RGBA display swatches."""
    if type(width) is not int or type(height) is not int:
        raise ValueError("Texture dimensions must be integers")
    if min(width, height) < 2 or max(width, height) > MAX_DIMENSION:
        raise ValueError("Texture dimension must be between 2 and 2048")
    defaults = options_for_color(color)
    if orientation_degrees is not None:
        defaults["orientation_degrees"] = orientation_degrees
    if repeats is not None:
        defaults["repeats"] = repeats
    options = options_for_color(dict(color, rendering={
        "strategy": "procedural_texture", **defaults,
    }))
    swatches = [parse_rgba(s) for s in color["rgba_swatches"]]
    angle = math.radians(options["orientation_degrees"])
    cx, cy = math.cos(angle), math.sin(angle)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # PNG scanline, filter 0
        vy = (y + 0.5) / height - 0.5
        for x in range(width):
            ux = (x + 0.5) / width - 0.5
            axis = ux * cx + vy * cy + 0.5
            if options["pattern"] == "uv_gradient" and options["repeats"] == 1:
                t = max(0.0, min(1.0, axis))
            else:
                t = (axis * options["repeats"]) % 1.0
            raw.extend(_sample(t, swatches, options["pattern"]))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + _chunk(b"IEND", b""))


def render_to_cache(color: dict, cache_dir: str | Path,
                    width: int = 512, height: int = 512, **overrides) -> Path:
    """Content-hash cache with atomic replacement. No external dependencies."""
    options = options_for_color(color)
    options.update(overrides)
    options = options_for_color(dict(color, rendering={
        "strategy": "procedural_texture", **options,
    }))
    payload = {"generator": GENERATOR_VERSION, "swatches": color["rgba_swatches"],
               "width": width, "height": height, "options": options}
    key = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / ("filamentra-" + key + ".png")
    if target.is_file():
        return target
    png = texture_png(color, width, height, **options)
    pending = None
    try:
        with tempfile.NamedTemporaryFile(dir=cache, suffix=".tmp",
                                         prefix=".filamentra-", delete=False) as file:
            pending = file.name
            file.write(png)
        os.replace(pending, target)
        return target
    finally:
        if pending and os.path.exists(pending):
            os.unlink(pending)
