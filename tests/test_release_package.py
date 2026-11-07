"""Regression tests for reproducible Filamentra runtime-source distributions."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("filamentra_release_builder",
                                               ROOT / "scripts" / "build_release.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ReleasePackageTests(unittest.TestCase):
    def test_generated_bytecode_and_tool_cache_do_not_change_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "filamentra"
            source.mkdir()
            (source / "__init__.py").write_text('"""Package."""\n', encoding="utf-8")
            assets = source / "assets"
            assets.mkdir()
            (assets / "profile.json").write_text('{"color": "blue"}\n', encoding="utf-8")

            previous_root = builder.ROOT
            try:
                builder.ROOT = root
                builder.main("1.2.3")
                archive = root / "dist" / "Filamentra-1.2.3.zip"
                original = archive.read_bytes()

                # Python tests and tooling can generate these after checkout.
                cache = source / "__pycache__"
                cache.mkdir()
                (cache / "__init__.cpython-312.pyc").write_bytes(b"binary cache")
                (source / "stray.pyc").write_bytes(b"bytecode")
                (source / ".DS_Store").write_bytes(b"Finder metadata")
                ruff = source / ".ruff_cache"
                ruff.mkdir()
                (ruff / "state").write_text("tool output", encoding="utf-8")
                pytest = source / ".pytest_cache"
                pytest.mkdir()
                (pytest / "README.md").write_text("test output", encoding="utf-8")
                builder.main("1.2.3")

                self.assertEqual(archive.read_bytes(), original)
                with zipfile.ZipFile(archive) as zipped:
                    self.assertEqual(sorted(zipped.namelist()), [
                        "filamentra/__init__.py", "filamentra/assets/profile.json",
                        "release.json",
                    ])
                checksum = archive.with_suffix(".zip.sha256").read_text(encoding="ascii")
                self.assertEqual(checksum,
                                 hashlib.sha256(original).hexdigest() + "  " + archive.name + "\n")
            finally:
                builder.ROOT = previous_root


if __name__ == "__main__":
    unittest.main()
