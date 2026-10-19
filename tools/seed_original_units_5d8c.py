#!/usr/bin/env python3
"""Create a deterministic test fixture from ORIGINAL Social Wars initial village.

ALWAYS operates on the isolated GitHub Actions checkout, never personal saves.
Character item IDs 1313/1358/1376 are verified in the original unit_patch.
These IDs are unit *item IDs*, not SWF DefineSprite character IDs.
"""
import argparse
import hashlib
import json
from pathlib import Path

UNITS = [
    ("splinter_mech", 1313, 52, 45, 1),
    ("bushwacker", 1358, 55, 45, 1),
    ("reaper_drone", 1376, 58, 45, 1),
    ("opponent_splinter", 1313, 61, 45, 3),
]

def seed(path, output):
    source = Path(path)
    village = json.loads(source.read_text(encoding="utf-8"))
    if not village.get("maps") or not isinstance(village["maps"][0]["items"], dict):
        raise ValueError("Unexpected initial village structure")
    items = village["maps"][0]["items"]
    occupied={(v[1],v[2]) for v in items.values()}
    original_count=len(items)
    available=max(int(k) for k in items)+1
    placements=[]
    for name, unit_id, x, y, player in UNITS:
        if (x,y) in occupied:
            raise ValueError("Fixture overlaps original map object at (%s,%s)"%(x,y))
        if not 0<=x<100 or not 0<=y<100:
            raise ValueError("Fixture outside test tile range")
        items[str(available)]=[unit_id,x,y,0,0,[],{},player]
        placements.append({"index":available,"name":name,"item_id":unit_id,
                           "map_tile":[x,y],"player_id":player})
        available+=1
    village["playerInfo"]["completed_tutorial"]=1
    target = Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(village,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    result={
        "fixture":"isolated_original_initial_village_5d8c",
        "source_template_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "generated_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
        "original_map_items":original_count,
        "seeded_units":placements,
        "sprite_identity_verified":False,
        "action_states_verified":False,
        "warning":"Unit item IDs are gameplay item references; no SWF sprite character ID has been identified."
    }
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--initial",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--manifest",required=True)
    args=ap.parse_args()
    manifest=seed(args.initial,args.out)
    Path(args.manifest).parent.mkdir(parents=True,exist_ok=True)
    Path(args.manifest).write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("UNIT_FIXTURE_5D8C",json.dumps(manifest))
