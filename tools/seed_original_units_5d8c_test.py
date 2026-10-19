#!/usr/bin/env python3
import json,tempfile,unittest
from pathlib import Path
from seed_original_units_5d8c import seed,UNITS

class SeedTests(unittest.TestCase):
 def test_reproducible_isolated_template(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);original=root/"initial.json";out=root/"seeded.json"
   base={"playerInfo":{"completed_tutorial":0},
     "maps":[{"items":{"1":[26,40,40,0,0,[],{},1]}}]}
   raw=json.dumps(base,sort_keys=True)
   original.write_text(raw)
   manifest=seed(original,out)
   new=json.loads(out.read_text())
   self.assertEqual(len(new["maps"][0]["items"]),1+len(UNITS))
   self.assertEqual(new["playerInfo"]["completed_tutorial"],1)
   self.assertEqual(json.loads(original.read_text()),base)
   self.assertFalse(manifest["sprite_identity_verified"])
   self.assertFalse(manifest["action_states_verified"])
   self.assertEqual([s["item_id"] for s in manifest["seeded_units"]],[1313,1358,1376,1313])
   self.assertEqual(manifest["generated_sha256"],seed(original,out)["generated_sha256"])
 def test_collision_guard(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=root/"initial.json"
   p.write_text(json.dumps({"playerInfo":{"completed_tutorial":0},
     "maps":[{"items":{"1":[26,52,45,0,0,[],{},1]}}]}))
   with self.assertRaisesRegex(ValueError,"overlaps"):
    seed(p,root/"after.json")
   self.assertFalse((root/"after.json").exists())

if __name__=="__main__":
 unittest.main(verbosity=2)
