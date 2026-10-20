#!/usr/bin/env python3
"""5D.8P two-axis acquisition threshold sweep for original auto-combat (disposable CI only).

Fixed Bushwacker and one hostile Reaper Drone seeded on vacant
tiles in a pristine original village. No artificial attack/damage is applied.
"""
import argparse
import hashlib
import json
from pathlib import Path

POSITIONS = {
    **{f"north_{d:02d}": (55, 45-d) for d in (16,17,18,19)},
    **{f"east_{d:02d}": (55+d, 45) for d in (16,17,18,19)},
}

def seed(source, target, scenario):
    if scenario not in POSITIONS: raise ValueError("unknown scenario")
    src, dst=Path(source), Path(target)
    if src.resolve()==dst.resolve(): raise ValueError("never overwrite input")
    original=src.read_bytes()
    village=json.loads(original)
    items=village["maps"][0]["items"]
    if len(items)!=40 or max(map(int,items))!=40: raise ValueError("unexpected pristine village")
    x,y=POSITIONS[scenario]
    placements=[
      ("attacker_bushwacker",41,1358,55,45,1),
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
        "lot":"5D.8P","scenario":scenario,
        "manhattan_distance_tiles":abs(x-55)+abs(y-45),
        "axis":scenario.split("_")[0],
        "source_template_sha256":hashlib.sha256(original).hexdigest(),
        "generated_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),
        "original_items":40,
        "seeded_units":[
            {"name":name,"index":idx,"item_id":item_id,"tile":[tx,ty],"owner":owner}
            for name,idx,item_id,tx,ty,owner in placements
        ],
        "attack_injected":False,"original_swf_modified":False,
        "notes":"SWF unchanged; enemy PlayerID=2; north and east distances 16-19 with no injected attack."
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
    print("AUTO_AGGRO_FIXTURE_5D8P",json.dumps(result))
