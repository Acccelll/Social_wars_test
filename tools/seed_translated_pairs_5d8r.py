#!/usr/bin/env python3
"""5D.8R translated unit-pair and focus-camera controls for original auto-combat (disposable CI only).

Fixed Bushwacker and one hostile Reaper Drone seeded on vacant
tiles in a pristine original village. No artificial attack/damage is applied.
"""
import argparse
import hashlib
import json
from pathlib import Path

# Pair coordinates: (attacker tile, enemy tile).
# Every target is initially exactly 15 orthogonal tiles away.
# Empty cells are verified against the 40-object original village before seeding.
POSITIONS = {
    "east_original": ((55,45),(70,45)),
    "north_original": ((55,45),(55,30)),
    "east_westshift": ((40,45),(55,45)),
    "east_northshift": ((55,35),(70,35)),
    "east_midshift": ((45,43),(60,43)),
}

def seed(source, target, scenario):
    if scenario not in POSITIONS: raise ValueError("unknown scenario")
    src, dst=Path(source), Path(target)
    if src.resolve()==dst.resolve(): raise ValueError("never overwrite input")
    original=src.read_bytes()
    village=json.loads(original)
    items=village["maps"][0]["items"]
    if len(items)!=40 or max(map(int,items))!=40: raise ValueError("unexpected pristine village")
    (bx,by),(x,y)=POSITIONS[scenario]
    placements=[
      ("attacker_bushwacker",41,1358,bx,by,1),
      ("hostile_reaper_drone",42,1376,x,y,2)
    ]
    occupied={(v[1],v[2]) for v in items.values()}
    for name,idx,item_id,tx,ty,owner in placements:
        if (tx,ty) in occupied: raise ValueError("overlaps existing object")
        occupied.add((tx,ty))
        items[str(idx)]=[item_id,tx,ty,0,0,[],{},owner]
    village["playerInfo"]["completed_tutorial"]=1
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(village,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {
        "lot":"5D.8R","scenario":scenario,
        "manhattan_distance_tiles":abs(x-bx)+abs(y-by),
        "axis":"north" if scenario=="north_original" else "east",
        "pair_translation":[bx-55,by-45],
        "source_template_sha256":hashlib.sha256(original).hexdigest(),
        "generated_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
        "original_items":40,
        "seeded_units":[
            {"name":name,"index":idx,"item_id":item_id,"tile":[tx,ty],"owner":owner}
            for name,idx,item_id,tx,ty,owner in placements
        ],
        "attack_injected":False,"original_swf_modified":False,
        "notes":"Original 40 village objects untouched; two unit items placed at exactly 15 tiles apart; no synthetic attack."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--pristine",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--scenario",choices=tuple(POSITIONS),required=True)
    p.add_argument("--manifest",required=True)
    a=p.parse_args()
    result=seed(a.pristine,a.out,a.scenario)
    m=Path(a.manifest);m.parent.mkdir(parents=True,exist_ok=True)
    m.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("TRANSLATED_PAIR_FIXTURE_5D8R",json.dumps(result))
