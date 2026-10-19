import tempfile,unittest
from pathlib import Path
from visual_gallery_5d6 import baseline_group,pick,gallery

class GalleryTests(unittest.TestCase):
 def test_category(self):
  self.assertEqual(baseline_group("1212_tetrapod_mech.swf"),"units")
  self.assertEqual(baseline_group("0022_tower_1_m.swf"),"buildings")
 def test_animated_preference(self):
  d={"sprites":[{"character_id":1,"declared_frames":1,"place_events":5,
                 "child_character_ids":[2]},
                {"character_id":3,"declared_frames":17,"place_events":8,
                 "child_character_ids":[7]}]}
  self.assertEqual(pick(d)["character_id"],3)
 def test_html_escaped(self):
  with tempfile.TemporaryDirectory() as tmp:
   gallery([{"category":"units","swf":"bad<script>.swf","id":8,
             "frames_declared":1,"children":[],"error":"<img>"}],Path(tmp))
   page=(Path(tmp)/"index.html").read_text()
   self.assertIn("&lt;script&gt;",page)
   self.assertIn("&lt;img&gt;",page)
   self.assertNotIn("<img>",page)
if __name__=="__main__":unittest.main(verbosity=2)
