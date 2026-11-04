import struct
import tempfile
import unittest
import zlib

from filamentra.texture_generator import parse_rgba, options_for_color, texture_png, render_to_cache


def read_pixels(png):
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    pos, w, h, body = 8, None, None, b""
    while pos < len(png):
        size = struct.unpack(">I", png[pos:pos + 4])[0]
        tag = png[pos + 4:pos + 8]
        data = png[pos + 8:pos + 8 + size]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", data[:8])
        elif tag == b"IDAT":
            body += data
        pos += size + 12
    buf = zlib.decompress(body)
    rows = []
    for y in range(h):
        line = buf[y * (w * 4 + 1):(y + 1) * (w * 4 + 1)]
        assert line[0] == 0
        rows.append([tuple(line[1 + x * 4:1 + x * 4 + 4]) for x in range(w)])
    return rows


DUAL = {"color_mode": "multicolor", "rgba_swatches": ["#FF0000FF", "#0000FFFF"]}
GRAD = {"color_mode": "gradient", "rgba_swatches": ["#FF0000FF", "#0000FFFF"]}


class TextureTests(unittest.TestCase):
    def test_parser(self):
        self.assertEqual(parse_rgba("#01020380"), (1, 2, 3, 128))
        with self.assertRaises(ValueError):
            parse_rgba("#fff")

    def test_bands(self):
        row = read_pixels(texture_png(DUAL, 32, 8))[1]
        self.assertEqual(row[0], (255, 0, 0, 255))
        self.assertEqual(row[-1], (0, 0, 255, 255))
        self.assertEqual(len(set(row)), 2)

    def test_orientation(self):
        rows = read_pixels(texture_png(DUAL, 16, 16, orientation_degrees=90))
        self.assertEqual(rows[1][0], rows[1][15])
        self.assertNotEqual(rows[1][0], rows[15][0])

    def test_gradient(self):
        row = read_pixels(texture_png(GRAD, 16, 4))[0]
        self.assertGreater(row[7][0], 0)
        self.assertGreater(row[7][2], 0)

    def test_multistop_and_alpha(self):
        c = {"color_mode": "gradient",
             "rgba_swatches": ["#FF000020", "#00FF0080", "#0000FFFF"]}
        px = read_pixels(texture_png(c, 64, 4))[0][31]
        self.assertGreater(px[1], px[0])
        self.assertGreater(px[1], px[2])
        self.assertTrue(32 <= px[3] <= 255)

    def test_cache(self):
        with tempfile.TemporaryDirectory() as root:
            a = render_to_cache(DUAL, root, 32, 32)
            b = render_to_cache(DUAL, root, 32, 32)
            c = render_to_cache(DUAL, root, 32, 32, orientation_degrees=90)
            self.assertEqual(a, b)
            self.assertNotEqual(a, c)
            self.assertEqual(a.read_bytes(), texture_png(DUAL, 32, 32))

    def test_validation(self):
        with self.assertRaises(ValueError):
            options_for_color({"color_mode": "solid", "rgba_swatches": ["#FF0000FF"]})
        with self.assertRaises(ValueError):
            texture_png(DUAL, 1, 8)
        with self.assertRaises(ValueError):
            texture_png(DUAL, 8, 8, repeats=0)
        with self.assertRaises(ValueError):
            texture_png(GRAD, 8, 8, orientation_degrees=float("nan"))
        with self.assertRaises(ValueError):
            options_for_color(dict(DUAL, rendering={"pattern": "uv_gradient"}))


if __name__ == "__main__":
    unittest.main()
