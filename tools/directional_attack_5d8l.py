#!/usr/bin/env python3
"""5D.8L — Original Bushwacker's five directional attack timelines.

Reads the SHA-pinned Social Wars 0.02a distribution, never writes a SWF.
Exports full 60-frame FFDec GIF *previews*, not runtime frame identity.
Builds a static placement/dependency audit and a 5x7 contact sheet.
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import tempfile
import time
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw, ImageFont
from visual_timelines import inspect

BASENAME="1358_bushwacker.swf"
SWF_BYTES=1158582
SWF_SHA="e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e"
MAIN_ID=1092
DIRECTIONS=[
    ("E",11,643,"_1358_bushwacker_fla.E_attack_133"),
    ("TE",12,675,"_1358_bushwacker_fla.TE_attack_141"),
    ("P",13,716,"_1358_bushwacker_fla.P_attack_145"),
    ("T",14,752,"_1358_bushwacker_fla.T_attack_153"),
    ("F",15,786,"_1358_bushwacker_fla.F_attack_159"),
]
SAMPLES=[1,6,7,12,13,16,19]


def from_original(archive):
    if Path(archive).stat().st_size!=492630085:
        raise ValueError("Original release size mismatch")
    with zipfile.ZipFile(archive) as z:
        found=[m for m in z.infolist() if not m.is_dir() and
               PurePosixPath(m.filename).name==BASENAME and
               "/assets/sprites/" in "/"+m.filename]
        if len(found)!=1:raise ValueError("Expected unique original Bushwacker SWF")
        m=found[0]
        if m.file_size!=SWF_BYTES:raise ValueError("Unexpected source SWF length")
        swf=z.read(m)
    if hashlib.sha256(swf).hexdigest()!=SWF_SHA:
        raise ValueError("Original SWF SHA mismatch")
    return m.filename,swf


def placement_at(events, frame, depth):
    events=[e for e in events if e["frame"]<=frame and e.get("depth")==depth]
    character=None
    for e in events:
        if e["op"]=="remove":character=None
        elif e["op"]=="place":
            character=e.get("character_id", e.get("resolved_character_id",character))
    return character


def static_analysis(t):
    sprites={s["character_id"]:s for s in t["sprites"]}
    main=sprites[MAIN_ID]
    labels={x["name"]:x["frame"] for x in main["frame_labels"]}
    if labels.get("ATAQUE")!=11:raise ValueError("Attack state label moved")
    rows=[]
    for direction,main_frame,cid,expected_name in DIRECTIONS:
        if cid not in sprites:raise ValueError(f"Missing DefineSprite {cid}")
        child=sprites[cid]
        if t["symbol_names"].get(str(cid))!=expected_name:
            raise ValueError("Source symbol name differs: "+direction)
        if placement_at(main["frame_events"],main_frame,1)!=cid:
            raise ValueError("Attack direction placement differs: "+direction)
        if child["declared_frames"]!=60 or child["parse_warnings"]:
            raise ValueError("Unexpected attack timeline structure: "+direction)
        frame_events=child["frame_events"]
        # These are *display-list change* statistics, not action or damage.
        placements=Counter(e["frame"] for e in frame_events if e["op"]=="place")
        removals=Counter(e["frame"] for e in frame_events if e["op"]=="remove")
        active_changes={
          frame:{
             "placements":placements[frame],
             "removals":removals[frame],
             "unique_direct_character_ids":sorted(set(
               e.get("character_id",e.get("resolved_character_id"))
               for e in frame_events if e["frame"]==frame and
               e["op"]=="place" and isinstance(e.get("character_id",e.get("resolved_character_id")),int)
             ))}
          for frame in range(1,61)
        }
        rows.append({
          "direction_tag":direction,
          "main_sprite_id":MAIN_ID,
          "main_attack_frame":main_frame,
          "attack_sprite_id":cid,
          "symbol_name":expected_name,
          "declared_frames":child["declared_frames"],
          "place_events":child["place_events"],
          "remove_events":child["remove_events"],
          "unique_direct_children":child["child_character_ids"],
          "direct_children_count":len(child["child_character_ids"]),
          "display_list_per_frame":active_changes
        })
    allsets=[set(r["unique_direct_children"]) for r in rows]
    shared=set.intersection(*allsets)
    union=set.union(*allsets)
    for r,children in zip(rows,allsets):
        r["shared_direct_child_ids"]=sorted(shared)
        r["direction_specific_direct_child_ids"]=sorted(children-set.union(*(s for s in allsets if s is not children)))
        # Inference guard: no projectile IDs are assigned from placement changes alone.
        r["projectile_id_confirmed"]=None
        r["effect_id_confirmed"]=None
    return {
       "root_sprite_id":MAIN_ID,
       "root_attack_state_label_frame":labels["ATAQUE"],
       "root_frames":main["declared_frames"],
       "directions":rows,
       "shared_direct_child_ids":sorted(shared),
       "all_direct_child_ids":sorted(union),
       "static_only":True,
       "limitation":"SymbolClass labels and static placements identify five attack direction clips; not projectile/impact identity or Ruffle runtime timing."
    }


def export(jar,src_swf,dir,entry):
    direction=entry["direction_tag"]
    sid=entry["attack_sprite_id"]
    dest=dir/direction;dest.mkdir(parents=True,exist_ok=True)
    # Same working FFDec CLI flags as 5D.8K; this time all 60 source frames.
    cmd=["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),"-cli",
         "-selectid",str(sid),"-select",f"{sid}:1-60",
         "-sublength","60","-format","sprite:gif",
         "-export","sprite",str(dest),str(src_swf)]
    start=time.monotonic()
    try:
        p=subprocess.run(cmd,text=True,capture_output=True,errors="replace",timeout=200)
        gifs=sorted(dest.rglob("*.gif"))
        (dir/(direction+".ffdec.log")).write_text((p.stdout+"\n"+p.stderr)[-3000:],encoding="utf-8")
        if p.returncode or not gifs:raise RuntimeError(f"FFDec failed for {direction}: exit={p.returncode}")
        gif=gifs[0]
        with Image.open(gif) as image:
            n=getattr(image,"n_frames",1)
            dims=list(image.size)
            image_hashes=[]
            for i in range(n):
                image.seek(i)
                image_hashes.append(hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest())
        distinct_count=len(set(image_hashes))
        # FFDec samples often loop the same shorter visual sequence.
        repeat=next((period for period in range(1,n//2+1)
                     if all(image_hashes[i]==image_hashes[i%period] for i in range(n))),None)
        return {"status":"EXPORTED","frames_in_gif":n,"gif_size":dims,
                "visually_distinct_frame_count":distinct_count,
                "preview_loop_period_frames":repeat,
                "gif_path":gif.relative_to(dir).as_posix(),
                "gif_sha256":hashlib.sha256(gif.read_bytes()).hexdigest(),
                "bytes":gif.stat().st_size,
                "duration_seconds":round(time.monotonic()-start,2)}
    except subprocess.TimeoutExpired:
        return {"status":"TIMEOUT","duration_seconds":round(time.monotonic()-start,2)}


def atlas(out,entries):
    w,h=255,235
    margin_x,margin_y=42,54
    bg=(236,235,228)
    canvas=Image.new("RGB",(margin_x+7*w+12,margin_y+5*h+10),bg)
    draw=ImageDraw.Draw(canvas)
    draw.text((10,6),"SOCIAL WARS 0.02a — ORIGINAL BUSHWACKER / ATTACK",fill=(32,41,48))
    for i,frame in enumerate(SAMPLES):
        draw.text((margin_x+i*w+10,29),f"Frame {frame:02d}",fill=(45,45,45))
    for row,entry in enumerate(entries):
        y=margin_y+row*h
        direction=entry["direction_tag"];status=entry["render"]["status"]
        draw.text((4,y+8),direction,fill=(30,40,70))
        if status!="EXPORTED":continue
        path=out/entry["render"]["gif_path"]
        with Image.open(path) as im:
            for i,sample in enumerate(SAMPLES):
                ix=min(sample-1,getattr(im,"n_frames",1)-1)
                im.seek(ix)
                sprite=im.convert("RGBA")
                sprite.thumbnail((w-16,h-20),Image.Resampling.LANCZOS)
                tile=Image.new("RGBA",(w-6,h-6),(250,250,246,255))
                tile.alpha_composite(sprite,((w-6-sprite.width)//2,(h-6-sprite.height)//2))
                canvas.paste(tile.convert("RGB"),(margin_x+i*w,y))
    out_file=out/"attack_direction_atlas.png"
    canvas.save(out_file,optimize=True)
    return out_file.name


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--ffdec",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    source,swf=from_original(a.archive)
    t=inspect(swf,True)
    if t["fps"]!=30 or t["sprite_count"]!=258 or t["totals"].get("parse_warnings"):
        raise ValueError("Static structure differs from original 5D.8K inventory")
    analysis=static_analysis(t)
    with gzip.open(out/"attack_timelines.json.gz","wt",encoding="utf-8") as f:
        json.dump({"source":source,"original_swf_sha256":SWF_SHA,
                   "analysis":analysis},f,ensure_ascii=False,separators=(",",":"))
    with tempfile.TemporaryDirectory(prefix="original-bushwacker-") as td:
        raw=Path(td)/BASENAME;raw.write_bytes(swf)
        for entry in analysis["directions"]:
            entry["render"]=export(a.ffdec,raw,out,entry)
            print("ORIGINAL_DIRECTION_5D8L",json.dumps({
              "direction":entry["direction_tag"],
              "sprite_id":entry["attack_sprite_id"],
              "child_count":entry["direct_children_count"],
              "render":entry["render"]},ensure_ascii=False),flush=True)
    preview=atlas(out,analysis["directions"])
    report={
      "lot":"5D.8L","source_swf":source,"sha256":SWF_SHA,
      "swf_unchanged":True,"fps":30,
      "main_sprite_id":1092,"attack_state_root_frames":[11,12,13,14,15],
      "directions":[{
          k:v for k,v in entry.items() if k not in ("display_list_per_frame","unique_direct_children","shared_direct_child_ids")}
          for entry in analysis["directions"]],
      "preview":preview,
      "all_five_gifs_exported":all(x["render"]["status"]=="EXPORTED" for x in analysis["directions"]),
      "projectile_define_sprite_confirmed":None,
      "impact_define_sprite_confirmed":None,
      "combat_video_correlation":"visual-only candidate matching pending; do not identify a sprite from similar shapes alone",
      "native_combat_evidence":"https://github.com/Acccelll/Social_wars_test/actions/runs/39353491847"
    }
    (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("5D8L_REPORT",json.dumps({
      "directions":[(x["direction_tag"],x["attack_sprite_id"],x["render"]["status"],x["render"].get("frames_in_gif"))
                    for x in analysis["directions"]],
      "atlas":preview, "projectile_verified":False
    }),flush=True)
if __name__=="__main__":main()
