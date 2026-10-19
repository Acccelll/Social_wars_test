#!/usr/bin/env python3
import tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
from analyze_runtime_5d8b import difference,analyze

class EvidenceTests(unittest.TestCase):
 def test_screenshots_are_not_gameproof(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   before=Image.new("RGB",(100,100),"black")
   before.save(root/"a.png")
   after=before.copy()
   ImageDraw.Draw(after).rectangle((20,20,80,80),fill="white")
   after.save(root/"b.png")
   rect={"x":0,"y":0,"width":100,"height":100}
   self.assertGreater(difference(root/"a.png",root/"b.png",rect),0.3)
   report={"events":[
    {"type":"begin_action","kind":"movement","wall_clock_ms":100,
     "player_bounds":rect},
    {"type":"end_action","kind":"movement","wall_clock_ms":200}
   ],"screenshots":[{"event_index":0,"file":"a.png"},{"event_index":1,"file":"b.png"}],
   "network_events":[{"path":"/static/socialwars/sprites/0022_tower_1_m.swf",
                      "wall_clock_ms":150}]}
   records=analyze(report,root)
   self.assertEqual(len(records),1)
   self.assertEqual(records[0]["visual_evidence"],"visual_change")
   self.assertFalse(records[0]["game_action_confirmed"])
   self.assertIsNone(records[0]["sprite_id_confirmed"])
   self.assertEqual(len(records[0]["requests_during_interval"]),1)
 def test_no_change_and_missing_images(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   Image.new("RGB",(50,50),"black").save(root/"a.png")
   rect={"x":0,"y":0,"width":50,"height":50}
   self.assertEqual(difference(root/"a.png",root/"a.png",rect),0)
   report={"events":[{"type":"begin_action","kind":"attack"},
                     {"type":"end_action","kind":"attack"}]}
   rows=analyze(report,root)
   self.assertEqual(rows[0]["visual_evidence"],"insufficient")
if __name__=="__main__":unittest.main(verbosity=2)
