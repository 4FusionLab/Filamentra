"""Offline adapter contract tests; not a real Fusion integration run."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from filamentra.appearance_mapping import resolve_appearance, preview_hex, haze_effective_roughness, resolve_catalog_color
from filamentra.fusion_appearance import install_resolved_appearance

class FakeFloatProperty:
    def __init__(self, value, units=""):
        self.value=value
        self.units=units
        self.isReadOnly=False
        self.hasMultipleValues=False

class FakeAppearance:
    def __init__(self,name,kind):
        self.name=name
        self.surface=kind
        self.color=None
        self.roughness=0.4
        self.normalTexture=""
        self.roughnessTexture=""
        self.colorTexture=""
        self.deleted=False
        properties={"transparent_ior":FakeFloatProperty(1.4),"transparent_distance":FakeFloatProperty(1.0,"cm")}
        self.appearanceProperties=SimpleNamespace(itemById=properties.get)
    def deleteMe(self):
        self.deleted=True

class FakeAppearances:
    def __init__(self):
        self.created=[]
    def add(self,name,surface):
        obj=FakeAppearance(name,surface)
        self.created.append(obj)
        return obj

class FakeUnitsManager:
    def convert(self,value,from_unit,to_unit):
        if (from_unit,to_unit)==("mm","cm"):
            return value/10.0
        raise ValueError("Unsupported units")

CORE=SimpleNamespace(
  Color=SimpleNamespace(create=lambda *args: args),
  AppearanceSurfaceTypes=SimpleNamespace(
    OpaqueAppearanceSurface=0,
    MetallicAppearanceSurface=1,
    TransparentAppearanceSurface=2
  )
)

class AppearanceMappingTests(unittest.TestCase):
    def test_inheritance(self):
        out=resolve_appearance(
          {"surface_type":"transparent","roughness":0.22,"transmission":0.4,"haze":0.8,"textures":{"normal_gl":"a.png"}},
          {"haze":0.55,"textures":{"roughness":"b.png"}},
          {"haze":0.35,"transmission":0.75})
        self.assertEqual((out["haze"],out["transmission"]),(0.35,0.75))
        self.assertEqual(out["textures"],{"normal_gl":"a.png","roughness":"b.png"})
        with self.assertRaises(ValueError): resolve_appearance({"surface_type":"opaque","transmission":0.5})
        with self.assertRaises(ValueError): resolve_appearance({"surface_type":"transparent","haze":1.1})

    def test_mapping(self):
        self.assertAlmostEqual(haze_effective_roughness(0.8,0.28),0.608)
        self.assertAlmostEqual(haze_effective_roughness(0.35,0.12),0.356)
        self.assertEqual(haze_effective_roughness(0,0.8),0.8)

    def test_clear(self):
        clear={"name":"Clear","rgba_swatches":["#00000000"]}
        self.assertEqual(preview_hex(clear),("#F6F9F7",True))
        line={"appearance_preset":"petg-translucent"}
        presets={"petg-translucent":{"appearance":{"surface_type":"transparent","transmission":0.75,"haze":0.35}}}
        result, hex_rgb, derived=resolve_catalog_color(line,clear,presets)
        self.assertEqual(result["haze"],0.35)
        self.assertTrue(derived)
        self.assertEqual(hex_rgb,"#F6F9F7")

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.design=SimpleNamespace(appearances=FakeAppearances(),unitsManager=FakeUnitsManager())

    def test_translucent_maps_and_qualifies(self):
        profile={"surface_type":"transparent","transmission":0.4,"haze":0.8,"roughness":0.28,
                 "ior":1.46,"attenuation_distance_mm":7.5}
        report=install_resolved_appearance(self.design,"Test PLA","#FFAA77",profile,core=CORE)
        self.assertEqual(report.appearance.surface,2)
        self.assertAlmostEqual(report.appearance.roughness,0.608)
        self.assertEqual(report.appearance.color,(255,170,119,255))
        self.assertAlmostEqual(report.appearance.appearanceProperties.itemById("transparent_ior").value,1.46)
        self.assertAlmostEqual(report.appearance.appearanceProperties.itemById("transparent_distance").value,0.75)
        self.assertIn("attenuation_distance_mm",report.exact)
        self.assertIn("haze",report.approximate)
        self.assertIn("transmission",report.approximate)
        self.assertFalse(report.full_fidelity)

    def test_clear_appearance(self):
        report=install_resolved_appearance(self.design,"PETG Clear","#F6F9F7",
          {"surface_type":"transparent","transmission":0.75,"haze":0.35,"roughness":0.12,"attenuation_distance_mm":75},core=CORE)
        self.assertAlmostEqual(report.appearance.roughness,0.356)
        self.assertAlmostEqual(report.appearance.appearanceProperties.itemById("transparent_distance").value,7.5)

    def test_haze_maps_texture_skip_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            (p/"rough.png").write_bytes(b"PNG")
            (p/"normal.png").write_bytes(b"PNG")
            profile={"surface_type":"transparent","transmission":0.55,"roughness":0.2,"haze":0.55,
                     "textures":{"normal_gl":"normal.png","roughness":"rough.png"}}
            report=install_resolved_appearance(self.design,"PETG","#123456",profile,texture_root=p,core=CORE)
            self.assertEqual(report.appearance.normalTexture,str(p/"normal.png"))
            self.assertEqual(report.appearance.roughnessTexture,"")
            self.assertIn("textures.roughness",report.unavailable)
            self.assertIn("haze",report.approximate)

    def test_opaque_alpha(self):
        report=install_resolved_appearance(self.design,"Opaque","#112233",
          {"surface_type":"opaque","roughness":0.3,"opacity":200},core=CORE)
        self.assertEqual(report.appearance.surface,0)
        self.assertEqual(report.appearance.color,(17,34,51,200))
        self.assertTrue(report.full_fidelity)

    def test_invalid_input_is_rejected_before_create(self):
        with self.assertRaises(ValueError):
            install_resolved_appearance(self.design,"Bad","#WRONG",
              {"surface_type":"transparent","haze":0.7},core=CORE)
        self.assertEqual(len(self.design.appearances.created),0)

if __name__=="__main__":
    unittest.main()
