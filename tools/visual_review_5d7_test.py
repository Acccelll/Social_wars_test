#!/usr/bin/env python3
import tempfile,unittest
from pathlib import Path
from PIL import Image
from visual_review_5d7 import classify_text,classify_evidence,duplicates,fingerprint

class ReviewTests(unittest.TestCase):
 def test_state_labels(self):
  self.assertEqual(classify_text("runCycle"),["movement"])
  self.assertEqual(classify_text("Attack_01"),["attack"])
  self.assertEqual(classify_text("_fla.Transform_5"),[])
  self.assertEqual(classify_text("megatank"),[])
 def test_metadata_only(self):
  node={"frame_labels":[{"name":"walk"}],
        "frame_events":[{"instance_name":"shoot_1"}],
        "child_character_ids":[]}
  result=classify_evidence(node,[{"frame_labels":[{"name":"death"}]}])
  self.assertEqual(set(result),{"movement","attack","destruction"})
 def test_duplicate_detection(self):
  a={"key":"tower#52","sha256":"identical","pixel_fingerprint":"same",
     "decoded_frames":2,"perceptual_hashes":["0"*16]*3}
  b={**a,"key":"workshop#52"}
  c={"key":"mech#3","sha256":"different","pixel_fingerprint":"other",
     "decoded_frames":3,"perceptual_hashes":["f"*16]*3}
  answer=duplicates([a,b,c])
  self.assertEqual(answer["exact_sha256"],[["tower#52","workshop#52"]])
  self.assertEqual(answer["near_candidates"],[])
 def test_gif_fingerprint(self):
  with tempfile.TemporaryDirectory() as folder:
   dest=Path(folder)/"frames.gif"
   frames=[Image.new("RGBA",(24,24),c)
           for c in [(255,0,0,255),(0,255,0,255),(0,0,255,255)]]
   frames[0].save(dest,save_all=True,append_images=frames[1:],
                  duration=100,loop=0)
   x=fingerprint(dest)
   self.assertEqual(x["decoded_frames"],3)
   self.assertEqual(len(x["perceptual_hashes"]),3)

if __name__=="__main__":unittest.main(verbosity=2)
