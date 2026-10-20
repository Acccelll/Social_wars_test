#!/usr/bin/env python3
"""5D.8K: export labeled animation states from the original SWF main sprites.

Only explicit FrameLabel names on verified 0.02a SWFs count as state names.
This is not a runtime animation->individual pixel/frame identification.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from visual_timelines import inspect

SOURCES={
  "bushwacker":{
    "name":"1358_bushwacker.swf","size":1158582,
    "sha256":"e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e",
    "item_id":1358,"root_sprite_id":1092},
  "reaper_drone":{
    "name":"1376_reaperDrone.swf","size":201043,
    "sha256":"c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83",
    "item_id":1376,"root_sprite_id":1654}
}
CORE_STATES={"QUIETO":1,"ANDAR":6,"ATAQUE":11,"MUERTE":16}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--ffdec",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    jar=Path(args.ffdec).resolve();out=Path(args.out).resolve()
    if not jar.is_file():raise ValueError("FFDec jar not found")
    out.mkdir(parents=True,exist_ok=True)
    summary={"lot":"5D.8K-states","original_swf_modified":False,
             "source_zip_size":Path(args.archive).stat().st_size,
             "states_source":"SWF DefineSprite/FrameLabel tags, verified parser",
             "states":{},
             "caveat":"GIF samples have 15 nested timeline subframes. Rendering is independent from actual execution; call-site and specific projectile IDs remain unverified."}
    with zipfile.ZipFile(args.archive) as z:
        for unit,cfg in SOURCES.items():
            hits=[m for m in z.infolist() if not m.is_dir() and
                  PurePosixPath(m.filename).name==cfg["name"] and
                  "/assets/sprites/" in "/"+m.filename]
            if len(hits)!=1:raise ValueError("Could not uniquely find original "+cfg["name"])
            m=hits[0];swf=z.read(m)
            sha=hashlib.sha256(swf).hexdigest()
            if m.file_size!=cfg["size"] or sha!=cfg["sha256"]:
                raise ValueError("Original SWF identity changed: "+unit)
            t=inspect(swf,True)
            sid=cfg["root_sprite_id"]
            assert t["root"]["child_character_ids"]==[sid], "Original root timeline changed"
            sprite=next(s for s in t["sprites"] if s["character_id"]==sid)
            labels=sprite["frame_labels"]
            label_map={row["name"]:row["frame"] for row in labels}
            if any(label_map.get(k)!=v for k,v in CORE_STATES.items()):
                raise ValueError("Original frame labels changed: "+unit)
            states=[]
            for i,label in enumerate(labels):
                first=label["frame"]
                last=min(sprite["declared_frames"],labels[i+1]["frame"]-1) if i+1<len(labels) else sprite["declared_frames"]
                if first>last:raise ValueError("Broken state frame bounds")
                states.append({"state":label["name"],"start_frame":first,
                               "end_frame":last,"sprite_character_id":sid,
                               "original_swf_sha256":sha})
            dir=out/unit;dir.mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="original-state-5d8k-") as td:
                swf_path=Path(td)/cfg["name"];swf_path.write_bytes(swf)
                for state in states:
                    if state["state"] not in CORE_STATES and unit=="bushwacker":
                        # The 01/02/03 directional variants are retained in metadata,
                        # but limit rendered exports to four core states.
                        state["render_status"]="METADATA_ONLY"
                        continue
                    label=state["state"]
                    start=time.monotonic()
                    dest=dir/label.lower()
                    dest.mkdir(parents=True,exist_ok=True)
                    cmd=["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),
                         "-cli","-selectid",str(sid),"-select",
                         f"{sid}:{state['start_frame']}-{state['end_frame']}",
                         "-sublength","15","-format","sprite:gif",
                         "-export","sprite",str(dest),str(swf_path)]
                    try:
                        proc=subprocess.run(cmd,capture_output=True,text=True,
                                            errors="replace",timeout=110)
                        gifs=sorted(dest.rglob("*.gif"))
                        state["render_status"]="EXPORTED" if proc.returncode==0 and gifs else "EMPTY_OR_ERROR"
                        state["ffdec_exit"]=proc.returncode
                        state["output_gifs"]=[{
                            "path":f.relative_to(out).as_posix(),
                            "size_bytes":f.stat().st_size
                        } for f in gifs[:10]]
                        (dir/(label.lower()+".ffdec.log")).write_text(
                            (proc.stdout+"\n"+proc.stderr)[-1800:],encoding="utf-8")
                    except subprocess.TimeoutExpired:
                        state["render_status"]="TIMEOUT"
                    state["elapsed_seconds"]=round(time.monotonic()-start,2)
                    print("5D8K_STATE",unit,label,
                          state["start_frame"],state["end_frame"],
                          state["render_status"],flush=True)
            summary["states"][unit]={
                "path":m.filename,"sha256":sha,"fps":t["fps"],
                "gameplay_item_id":cfg["item_id"],
                "root_sprite_character_id":sid,
                "declared_frames":sprite["declared_frames"],
                "frame_labels":states,
                "confirmed_state_labels":list(label_map.keys())}
    (out/"states_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    print("5D8K_STATES_SUMMARY",json.dumps({name:{
        "root_id":x["root_sprite_character_id"],
        "labels":x["confirmed_state_labels"],
        "rendered":sum(y.get("render_status")=="EXPORTED" for y in x["frame_labels"])}
        for name,x in summary["states"].items()},ensure_ascii=False),flush=True)
    return summary

if __name__=="__main__":
    main()
