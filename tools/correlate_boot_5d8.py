#!/usr/bin/env python3
"""Join browser-observed asset HTTP requests to archived preview SWF sources.

Does NOT prove an animation played or that a character ID was instanced.
A request is evidence of resource access only.
"""
import argparse
import csv
import json
from pathlib import Path

def correlate(runtime, gallery):
    paths=set(runtime["request_paths"])
    rows=[]
    for item in gallery["items"]:
        rel=item["source"].removeprefix("assets/")
        endpoint="/static/socialwars/"+rel
        rows.append({
            "source_swf":item["source"],
            "sprite_id":item["id"],
            "catalog_category":item["category"],
            "requested_during_boot":endpoint in paths,
            "requested_resource_path":endpoint if endpoint in paths else "",
            "observed_action":"",
            "runtime_sprite_identity_verified":False,
            "evidence_type":"http_resource_requested" if endpoint in paths else
                             "not_observed_in_boot_window",
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runtime-report",required=True)
    ap.add_argument("--catalog",default="data/visual/gallery_5d6.json")
    ap.add_argument("--out",default="dist/original-observation")
    args=ap.parse_args()
    output=Path(args.out);output.mkdir(parents=True,exist_ok=True)
    runtime=json.loads(Path(args.runtime_report).read_text(encoding="utf-8"))
    gallery=json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    rows=correlate(runtime,gallery)
    counts={
        "catalog_sprites":len(rows),
        "catalog_source_swfs":len(set(r["source_swf"] for r in rows)),
        "sprites_whose_swf_was_requested":sum(r["requested_during_boot"] for r in rows),
        "source_swfs_requested":len({r["source_swf"] for r in rows if r["requested_during_boot"]}),
        "sprite_actions_confirmed":0
    }
    columns=list(rows[0]) if rows else []
    with (output/"runtime_boot_presence_5d8.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader();w.writerows(rows)
    result={
        "method":"HTTP resource URL match against archive SWF path",
        "scope":"bootstrap-only; not an animation-state observation",
        "counts":counts,
        "records":rows,
        "warning":"Requesting an SWF does NOT prove its character ID rendered or played."
    }
    (output/"runtime_boot_presence_5d8.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("ORIGINAL_BOOT_ASSET_MATCH",json.dumps(counts),flush=True)

if __name__=="__main__":
    main()
