#!/usr/bin/env python3
"""5D.8U — extract Bushwacker/Reaper Drone server-effective unit stats.

Sources are the AcidCaos community recreation's main config + active unit_patch.
Do not incorrectly label these values as proven 2012 production server stats.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

IDS=(1358,1376)
FIELDS=("id","name","img_name","group_type","life","attack","defense",
        "attack_range","attack_interval","velocity","best_against",
        "best_against_mult","properties")
NUMERIC=("id","life","attack","defense","attack_range","attack_interval",
         "velocity","best_against_mult")

def fingerprint(raw):
    return hashlib.sha256(raw).hexdigest()

def parse_item(item):
    d={}
    for k in FIELDS:
        if k not in item:
            raise ValueError(f"Missing {k} in item {item.get('id')}")
        d[k]=int(item[k]) if k in NUMERIC else item[k]
    try:
        d["properties"]=json.loads(d["properties"])
    except (ValueError,TypeError) as e:
        raise ValueError("Unit properties not valid JSON") from e
    return d

def main():
    p=argparse.ArgumentParser()
    for a in ("base","patch","csv","patch_list","out"):
        p.add_argument("--"+a,required=True)
    a=p.parse_args()
    base_raw=Path(a.base).read_bytes()
    patch_raw=Path(a.patch).read_bytes()
    csv_raw=Path(a.csv).read_bytes()
    patches_raw=Path(a.patch_list).read_bytes()
    base=json.loads(base_raw)
    patch=json.loads(patch_raw)
    if not isinstance(base.get("items"),list) or not isinstance(patch,list):
        raise ValueError("Malformed server config")
    active=[line.split("#")[0].strip() for line in patches_raw.decode().splitlines()]
    if "unit_patch" not in active:
        raise ValueError("unit_patch is not active")
    by_id={}
    for item in base["items"]:
        if str(item.get("id")) in ("1358","1376"):
            by_id[int(item["id"])]=item
    original_ids=sorted(by_id)
    for change in patch:
        if change.get("op")!="add" or change.get("path")!="/items/-":
            raise ValueError("Unexpected patch operation")
        item=change["value"]
        if str(item.get("id")) in ("1358","1376"):
            by_id[int(item["id"])]=item
    if set(by_id)!=set(IDS):
        raise ValueError(f"Unit IDs missing: {set(IDS)-set(by_id)}")
    text=csv_raw.decode("utf-8-sig")
    rows=list(csv.reader(io.StringIO(text),delimiter="\t"))
    csv_matches={int(row[0]):row for row in rows if row and row[0] in {"1358","1376"}}
    if set(csv_matches)!=set(IDS):
        raise ValueError("Expected two unit CSV entries")
    units={str(id):parse_item(by_id[id]) for id in IDS}
    for id in IDS:
        row=csv_matches[id]
        expected={"life":3,"attack":4,"attack_range":5,"velocity":6,"attack_interval":7}
        for field,index in expected.items():
            if int(row[index])!=units[str(id)][field]:
                raise ValueError(f"Unit patch CSV mismatch id={id} field={field}")
        if units[str(id)]["attack_interval"]<=0 or units[str(id)]["life"]<=0:
            raise ValueError("Invalid attack interval or max HP")
    output={
      "lot":"5D.8U",
      "source_project":"AcidCaos/socialwarriors",
      "source_type":"community-maintained reconstructed server configuration",
      "historical_authenticity":"Values verified in the server's ACTIVE unit_patch and generated effective item mapping; not independent proof of the historical production backend.",
      "base_config_original_ids":original_ids,
      "item_resolution":"Last applied /items/- patch entry overrides earlier matching IDs, matching duplicate cleanup in get_game_config.py",
      "units":units,
      "source_sha256":{
        "config/main.json":fingerprint(base_raw),
        "config/patch/unit_patch.json":fingerprint(patch_raw),
        "config/patch/patches.txt":fingerprint(patches_raw),
        "tools/sw_unit_patch.csv":fingerprint(csv_raw)
      },
      "explicit_caveats":[
        "These are canonical values of the community reconstruction server after active patches.",
        "Original SWF classes implement combat formulas but do not independently authenticate modern patch stat values.",
        "attack_interval is a configuration number; its game-time unit requires confirmation from the original ActionScript.",
        "Visual demo uses separately drawn Canvas shapes, not proprietary sprite frames."
      ]
    }
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n")
    print("SERVER_UNIT_STATS_5D8U",json.dumps({
      "base_ids":original_ids,
      "units":{k:{f:v[f] for f in ("life","attack","defense","attack_range","attack_interval","velocity")} for k,v in units.items()},
      "source_hashes":output["source_sha256"]
    }))
if __name__=="__main__":
    main()
