#!/usr/bin/env python3
"""5D.8K read-only correlation candidates: original unit SWF timelines + bounded FFDec previews.

Only canonical Social Wars 0.02a archive from an isolated job.
A rendered animated sprite is only a *candidate*, not evidence of runtime state.
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from visual_timelines import inspect

ASSETS = {
    "bushwacker": ("1358_bushwacker.swf", 1358, 1158582),
    "reaper_drone": ("1376_reaperDrone.swf", 1376, 201043),
}
COMBAT_HINTS = re.compile(r"shoot|shot|gun|attack|fire|dead|die|death|hit|hurt|damage|bullet|projectile|impact|blast|explos|weapon|walk|move|idle", re.I)
MAX_SWF_BYTES = 5_000_000


def candidates(swf):
    names = swf["symbol_names"]
    root_children = set(swf["root"].get("child_character_ids", []))
    scored = []
    for sprite in swf["sprites"]:
        sid = sprite["character_id"]
        label = names.get(str(sid), sprite.get("symbol_name", ""))
        frames = sprite["declared_frames"]
        complexity = sprite["place_events"] + sprite["remove_events"]
        matches = COMBAT_HINTS.findall(label)
        labeled = [x for x in sprite.get("frame_labels", [])
                   if COMBAT_HINTS.search(x.get("name", ""))]
        # Heuristic ranking, not class or animation state identification.
        score = (60 if matches else 0) + (40 if labeled else 0)
        score += 8 if sid in root_children else 0
        score += min(max(frames-1, 0), 20)*2 + min(complexity, 100)/20
        scored.append({
           "sprite_character_id": sid, "symbol_name": label,
           "frames": frames, "placements": sprite["place_events"],
           "removals": sprite["remove_events"],
           "root_referenced": sid in root_children,
           "frame_labels": sprite.get("frame_labels", []),
           "combat_name_or_frame_label": bool(matches or labeled),
           "static_candidate_score": round(score, 2)
        })
    return sorted(scored,key=lambda x:(-x["static_candidate_score"],-x["frames"],x["sprite_character_id"]))


def ffdec_export(jar, swf_file, out, selected, timeout):
    if not selected:
        return {"status":"NO_CANDIDATES"}
    ids = ",".join(str(x["sprite_character_id"]) for x in selected)
    selection = ",".join(f"{x['sprite_character_id']}:1-{min(4,x['frames'])}" for x in selected)
    # "sprite:gif" preserves animation across frames. Nested active timelines are
    # rendered as a bounded sample (12 subframes), not the full state machine.
    cmd=["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),"-cli",
         "-selectid",ids,"-select",selection,"-sublength","12",
         "-format","sprite:gif","-export","sprite",str(out),str(swf_file)]
    out.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,errors="replace",timeout=timeout)
        status="EXPORTED" if r.returncode==0 else "FFDEC_ERROR"
        output=(r.stdout+"\n"+r.stderr)
        (out.parent/"ffdec.log").write_text(output[-12000:],encoding="utf-8")
        files=sorted(p for p in out.rglob("*") if p.is_file())
        return {"status":status,"returncode":r.returncode,
                "seconds":round(time.monotonic()-start,2),
                "selected_sprite_ids":[x["sprite_character_id"] for x in selected],
                "files":[{"file":p.relative_to(out.parent).as_posix(),
                          "size_bytes":p.stat().st_size} for p in files][:30]}
    except subprocess.TimeoutExpired:
        return {"status":"TIMEOUT","seconds":round(time.monotonic()-start,2),
                "selected_sprite_ids":[x["sprite_character_id"] for x in selected]}


def analyze(archive, jar, out, render=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest={"lot":"5D.8K","source":"Social Wars 0.02a original distribution",
              "original_swf_unchanged":True,
              "original_combat_run":"https://github.com/Acccelll/Social_wars_test/actions/runs/39353491847",
              "items":{}, "warnings":[],
              "important_limit":"SWF static DefineSprite IDs are file-local. Exported samples are NOT yet matched to the runtime gun/impact/death pixels."}
    with zipfile.ZipFile(archive) as z:
        members=[m for m in z.infolist() if not m.is_dir()]
        for unit,(name,item_id,expected_bytes) in ASSETS.items():
            hits=[m for m in members if PurePosixPath(m.filename).name==name
                  and "/assets/sprites/" in "/"+m.filename]
            if len(hits)!=1:
                raise ValueError(f"{name}: expected one original sprite asset, got {len(hits)}")
            member=hits[0]
            if member.file_size!=expected_bytes or member.file_size>MAX_SWF_BYTES:
                raise ValueError(f"{name}: original source size changed")
            data=z.read(member)
            sha=hashlib.sha256(data).hexdigest()
            t=inspect(data,detailed=True)
            ranked=candidates(t)
            unit_out=out/unit;unit_out.mkdir(exist_ok=True)
            with gzip.open(unit_out/"timeline.json.gz","wt",encoding="utf-8") as f:
                json.dump({"path":member.filename, "item_id":item_id, "sha256":sha,
                           "timeline":t},f,ensure_ascii=False,separators=(",",":"))
            with (unit_out/"candidates.csv").open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=["sprite_character_id","symbol_name",
                  "frames","placements","removals","root_referenced",
                  "combat_name_or_frame_label","static_candidate_score"])
                w.writeheader()
                for row in ranked:w.writerow({k:row.get(k) for k in w.fieldnames})
            sample=[r for r in ranked if r["frames"]>1][:3]
            if not sample:
                sample=ranked[:3]
            rec={
              "path":member.filename, "item_id":item_id, "sha256":sha,
              "source_size_bytes":member.file_size,
              "fps":t["fps"],"stage_frames":t["stage_frames"],
              "sprite_count":t["sprite_count"],
              "declared_sprite_frames":t["totals"].get("sprite_frames_declared"),
              "parse_warnings":t["totals"].get("parse_warnings",0),
              "named_symbols":len(t["symbol_names"]),
              "root_children":len(t["root"].get("child_character_ids",[])),
              "frame_label_count":sum(len(s.get("frame_labels",[])) for s in t["sprites"]),
              "combat_named_or_labeled_count":sum(r["combat_name_or_frame_label"] for r in ranked),
              "top_candidates":ranked[:12], "rendered_candidates":sample,
            }
            if render:
                with tempfile.TemporaryDirectory(prefix="original-unit-") as td:
                    swf_path=Path(td)/name
                    swf_path.write_bytes(data)
                    rec["export"]=ffdec_export(jar,swf_path,unit_out/"gif_samples",sample,150)
            manifest["items"][unit]=rec
            print("5D8K_UNIT",json.dumps({key:rec[key] for key in (
                "path","source_size_bytes","fps","sprite_count",
                "declared_sprite_frames","named_symbols",
                "frame_label_count","combat_named_or_labeled_count")},
                ensure_ascii=False),flush=True)
            print("5D8K_RANK",unit,json.dumps([{
              "sprite_character_id":r["sprite_character_id"],
              "frames":r["frames"],"symbol_name":r["symbol_name"],
              "score":r["static_candidate_score"]}
              for r in ranked[:8]],ensure_ascii=False),flush=True)
            if render:print("5D8K_RENDER",unit,json.dumps(rec["export"]),flush=True)
    (out/"summary.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--ffdec",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--skip-render",action="store_true")
    a=p.parse_args()
    analyze(a.archive,a.ffdec,a.out,not a.skip_render)
