#!/usr/bin/env python3
"""Test protocol and safety rules without touching any actual save."""
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs
from original_move_probe_5d8e import build_command,choose_destination,run

class OriginalMoveProbeTest(unittest.TestCase):
    def test_protocol_wire_format(self):
        values=parse_qs(build_command(41,[53,46]))
        self.assertEqual(values["USERID"],["{USERID}"])
        serialized=values["data"][0]
        self.assertEqual(len(serialized.split(";",1)[0]),64)
        payload=json.loads(serialized.split(";",1)[1])
        self.assertEqual(payload["commands"],[[0,"move",[41,53,46,0,""],[0]*8]])
    def test_avoid_occupied_destination(self):
        self.assertEqual(choose_destination([1313,52,45],{(53,46)}),[51,46])
    def test_refuse_any_non_loopback_host(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            fixture=d/"fixture.json"
            fixture.write_text(json.dumps({"seeded_units":[{"index":41,"item_id":1313,
                                                                "map_tile":[52,45]}]}))
            with self.assertRaisesRegex(ValueError,"loopback"):
                run("https://example.org",d,fixture)
            with self.assertRaisesRegex(ValueError,"loopback"):
                run("http://192.168.0.1:5055",d,fixture)
    def test_refuse_existing_save_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            (d/"existing.save.json").write_text("{}")
            fixture=d/"fixture.json"
            fixture.write_text(json.dumps({"seeded_units":[{"index":41,"item_id":1313,
                                                                "map_tile":[52,45]}]}))
            with self.assertRaisesRegex(ValueError,"not empty"):
                run("http://127.0.0.1:5055",d,fixture)

if __name__=="__main__":
    unittest.main(verbosity=2)
