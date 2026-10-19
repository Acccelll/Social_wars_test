#!/usr/bin/env python3
"""5D.8F pure tests: class list parsing, method indexing, immutable ZIP hash."""
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path
from tutorial_as3_probe_5d8f import CLASS_MATCH,METHOD_MATCH,summarize_scripts,extract_original

class TutorialProbeTests(unittest.TestCase):
    def test_fully_qualified_class_candidates(self):
        content="core.popup.PopupTutorialMC\ncore.tutorial.TutorialMain\nTutorialMain\n"
        self.assertEqual({m.group() for m in CLASS_MATCH.finditer(content)},
                         {"core.popup.PopupTutorialMC","core.tutorial.TutorialMain","TutorialMain"})
    def test_ignore_similar_names(self):
        self.assertEqual(CLASS_MATCH.findall("DummyPopupTutorialMC2 UtilsTutorialMainFoo"),[])
    def test_index_methods_and_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            f=root/"core"/"PopupTutorialMC.as"
            f.parent.mkdir(parents=True)
            f.write_text("""package core {
                class PopupTutorialMC {
                  public function PopupTutorialMC() {}
                  private function closeWindow(event:MouseEvent):void {}
                  public override function onClick():void {}
                }
            }""")
            rows=summarize_scripts(root)
            self.assertEqual(len(rows),1)
            self.assertIn("closeWindow",rows[0]["method_names"])
            self.assertIn("onClick",rows[0]["method_names"])
            self.assertGreater(rows[0]["target_occurrences"]["MouseEvent"],0)
    def test_reject_non_original_checksum(self):
        with tempfile.TemporaryDirectory() as temp:
            z=Path(temp)/"faux.zip"
            with zipfile.ZipFile(z,"w") as f:
                f.writestr("social-warriors_0.02a/assets/flash/Basesec_1.5.4.swf",b"FWS"+"x"*25)
            with self.assertRaisesRegex(ValueError,"Unexpected Basesec SHA256"):
                extract_original(z,Path(temp)/"temp.swf")

if __name__=="__main__":
    unittest.main(verbosity=2)
