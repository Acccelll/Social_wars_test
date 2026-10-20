#!/usr/bin/env python3
"""5D.8H: isolated, disposable original-client test village with ONE added unit.

Read a pristine initial.json snapshot for EACH scenario. No personal saves. This
deliberately proves game-item index only; it does not invent a SWF DefineSprite ID.
"""
import argparse
import hashlib
import json
from pathlib import Path

SCENARIOS = {
    "splinter": ("splinter_mech", 1313),
    "bushwacker": ("bushwacker", 1358),
    "reaper": ("reaper_drone", 1376),
}
TEST_TILE = (55, 45)


def seed(source: Path, target: Path, scenario: str) -> dict:
    if scenario not in SCENARIOS:
        raise ValueError("Unknown scenario")
    if source.resolve() == target.resolve():
        raise ValueError("Pristine input cannot be overwritten")
    original_bytes = source.read_bytes()
    village = json.loads(original_bytes)
    items = village["maps"][0]["items"]
    if len(items) != 40 or max(int(k) for k in items) != 40:
        raise ValueError("Expected pristine original initial village of 40 items")
    if any(row[1:3] == list(TEST_TILE) for row in items.values()):
        raise ValueError("Test tile occupied in original")
    name, item_id = SCENARIOS[scenario]
    new_index = max(map(int, items)) + 1
    items[str(new_index)] = [item_id, *TEST_TILE, 0, 0, [], {}, 1]
    village["playerInfo"]["completed_tutorial"] = 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(village, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return {
        "fixture": f"original_5d8h_{scenario}_single_unit",
        "scenario": scenario,
        "source_template_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "generated_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "original_map_items": 40,
        "seeded_units": [{
            "index": new_index,
            "name": name,
            "item_id": item_id,
            "map_tile": list(TEST_TILE),
            "player_id": 1
        }],
        "original_swf_modified": False,
        "sprite_define_id": None,
        "warning": "Item index is not a DefineSprite character ID."
    }


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pristine",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--scenario",required=True,choices=tuple(SCENARIOS))
    p.add_argument("--manifest",required=True)
    a=p.parse_args()
    r=seed(Path(a.pristine),Path(a.out),a.scenario)
    m=Path(a.manifest)
    m.parent.mkdir(parents=True,exist_ok=True)
    m.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print("ISOLATED_5D8H",json.dumps(r))
