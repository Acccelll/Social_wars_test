#!/usr/bin/env python3
import struct
import unittest
import zlib
from visual_timelines import inspect,place,encode_tag

def fixture(compressed=False):
    sprite=(struct.pack("<HH",42,2)+
            encode_tag(4,struct.pack("<HH",7,3)+b"\0")+
            encode_tag(1,b"")+
            encode_tag(28,struct.pack("<H",3))+
            encode_tag(43,b"end\0")+
            encode_tag(1,b"")+b"\0\0")
    root=(encode_tag(39,sprite)+
          encode_tag(76,struct.pack("<HH",1,42)+b"robot\0")+
          encode_tag(4,struct.pack("<HH",42,1)+b"\0")+
          encode_tag(1,b"")+
          encode_tag(28,struct.pack("<H",1))+
          encode_tag(1,b"")+b"\0\0")
    body=b"\x08\0"+struct.pack("<HH",24*256,2)+root
    sig=b"CWS" if compressed else b"FWS"
    return sig+b"\x0a"+struct.pack("<I",len(body)+8)+(
        zlib.compress(body) if compressed else body)

class TimelineTest(unittest.TestCase):
    def test_two_formats(self):
        for compressed in [False,True]:
            r=inspect(fixture(compressed),True)
            self.assertEqual(r["fps"],24)
            self.assertEqual(r["stage_frames"],2)
            self.assertEqual(r["root"]["show_frames"],2)
            self.assertEqual(r["root"]["child_character_ids"],[42])
            self.assertEqual(r["sprite_count"],1)
            s=r["sprites"][0]
            self.assertEqual(s["declared_frames"],2)
            self.assertEqual(s["show_frames"],2)
            self.assertEqual(s["child_character_ids"],[7])
            self.assertEqual(s["symbol_name"],"robot")
            self.assertEqual(s["frame_events"][0]["frame"],1)
            self.assertEqual(s["frame_events"][0]["matrix"]["tx_twips"],0)
            self.assertEqual(s["frame_events"][1]["frame"],2)
            self.assertEqual(s["frame_labels"][0]["name"],"end")
    def test_place2_move(self):
        v=place(26,b"\x01"+struct.pack("<H",5))
        self.assertTrue(v["move"])
        self.assertEqual(v["depth"],5)
        self.assertNotIn("character_id",v)
    def test_place3(self):
        v=place(70,b"\x02\x00"+struct.pack("<HH",5,42))
        self.assertEqual(v["character_id"],42)
    def test_bad_trailer(self):
        with self.assertRaises(ValueError):
            inspect(fixture()[:-5])
if __name__=="__main__":
    unittest.main(verbosity=2)
