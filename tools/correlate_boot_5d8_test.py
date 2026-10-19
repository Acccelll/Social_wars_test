#!/usr/bin/env python3
import unittest
from correlate_boot_5d8 import correlate

class CorrelationTests(unittest.TestCase):
 def test_requested_file_not_sprite_id(self):
  runtime={"request_paths":["/static/socialwars/sprites/0022_tower_1_m.swf"]}
  gallery={"items":[
    {"source":"assets/sprites/0022_tower_1_m.swf","id":52,"category":"buildings"},
    {"source":"assets/sprites/0022_tower_1_m.swf","id":85,"category":"buildings"},
    {"source":"assets/sprites/1313_splinterMech.swf","id":189,"category":"units"}]}
  rows=correlate(runtime,gallery)
  self.assertEqual([x["requested_during_boot"] for x in rows],[True,True,False])
  self.assertTrue(all(not x["runtime_sprite_identity_verified"] for x in rows))
  self.assertTrue(all(not x["observed_action"] for x in rows))
 def test_never_match_similar_filename(self):
  runtime={"request_paths":["/static/socialwars/sprites/0022_tower_1_m.swf?bad"]}
  gallery={"items":[{"source":"assets/sprites/0022_tower_1_m.swf",
                     "id":52,"category":"buildings"}]}
  self.assertFalse(correlate(runtime,gallery)[0]["requested_during_boot"])
if __name__=="__main__":unittest.main(verbosity=2)
