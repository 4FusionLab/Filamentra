"""Build a deterministic source distribution with a numeric GitVersion identity."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main(version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise SystemExit("Expected GitVersion MajorMinorPatch.")
    source = ROOT / "filamentra"
    # The unit tests import Filamentra before packaging, creating local __pycache__.
    # Do not ship machine-specific bytecode or test/tool caches with the source ZIP.
    ignored_dirs = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
    ignored_suffixes = {".pyc", ".pyo"}
    paths = []
    for path in source.rglob("*"):
        if path.is_symlink():
            raise SystemExit("Unsafe Filamentra source symlink: " + str(path))
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if (any(part in ignored_dirs for part in relative.parts)
                or path.suffix in ignored_suffixes or path.name == ".DS_Store"):
            continue
        paths.append(path)
    paths.sort(key=lambda path: path.relative_to(ROOT).as_posix())
    if not paths:
        raise SystemExit("Missing Filamentra source.")
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    target = out / f"Filamentra-{version}.zip"
    metadata = {"product": "Filamentra", "version": version,
                "commit": os.environ.get("GITHUB_SHA", "")}
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as z:
        for path in paths:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, path.read_bytes())
        z.writestr(zipfile.ZipInfo("LICENSE", (2026, 1, 1, 0, 0, 0)), (ROOT / "LICENSE").read_bytes())
        info = zipfile.ZipInfo("release.json", (2026, 1, 1, 0, 0, 0))
        z.writestr(info, json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert json.loads(z.read("release.json"))["version"] == version
    checksum = target.with_suffix(".zip.sha256")
    checksum.write_text(hashlib.sha256(target.read_bytes()).hexdigest() +
                        "  " + target.name + "\n", encoding="ascii")
    print(target, checksum)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    main(args.version)
