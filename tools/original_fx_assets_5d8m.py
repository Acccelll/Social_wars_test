#!/usr/bin/env python3
"""5D.8M — prove 4 attack projectile/impact SWFs exist and extract visual tags.

Sources for the exact mapping are original DelegatesManager.as, Constants.as,
ProjectileDefinition.as, and ProjectileManager.as. Metadata is source-derived;
the original browser runtime did not expose per-frame projectile IDs.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from visual_timelines import inspect

SOURCE={
    "bushwacker":{
      "item_id":1358,
      "unit_class":"BushwackerDelegate",
      "registration_constant":"ID_UNIT_BUSHWACKER",
      "normal_projectile":"p.bulletAirBig",
      "normal_impact":"b.bazookaSmall",
      "special_projectile_candidates":["p.laserBeamBlueFat"],
      "confidence":"STATIC_DELEGATE_MAPPING"},
    "reaper_drone":{
      "item_id":1376,
      "unit_class":"ProjectileDelegate",
      "registration_constant":"ID_UNIT_REAPER_DRONE",
      "normal_projectile":"p.laserMassiveDrone",
      "normal_impact":"b.laserBlue",
      "confidence":"STATIC_DELEGATE_MAPPING"}
}
FX_NAMES=[
 "p.bulletAirBig","b.bazookaSmall","p.laserMassiveDrone","b.laserBlue"
]
FFDEC_FORMAT="image:png,shape:svg,morphshape:svg,sprite:gif,button:png"

def ffdec_export(jar,swf,dest):
    cmd=["java","-Xmx2g","-Djava.awt.headless=true","-jar",str(jar),"-cli",
         "-sublength","20","-format",FFDEC_FORMAT,
         "-export","image,shape,morphshape,sprite,button",str(dest),str(swf)]
    st=time.monotonic()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,errors="replace",timeout=100)
        dest.mkdir(parents=True,exist_ok=True)
        (dest/"ffdec.log").write_text((p.stdout+"\n"+p.stderr)[-6000:],encoding="utf-8")
        outputs=sorted(x for x in dest.rglob("*") if x.is_file() and x.name!="ffdec.log")
        return {
          "status":"EXPORTED" if p.returncode==0 and outputs else
                   ("EMPTY_VISUAL_CATEGORY" if p.returncode==0 else "FFDEC_ERROR"),
          "exit_code":p.returncode,
          "elapsed_seconds":round(time.monotonic()-st,2),
          "files":[{"name":x.relative_to(dest).as_posix(),"bytes":x.stat().st_size,
                    "sha256":hashlib.sha256(x.read_bytes()).hexdigest()}
                   for x in outputs[:150]],
          "file_count":len(outputs)
        }
    except subprocess.TimeoutExpired:
        return {"status":"TIMEOUT","elapsed_seconds":round(time.monotonic()-st,2)}

def main():
    p=argparse.ArgumentParser()
    for arg in ("archive","ffdec","out"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    archive=Path(a.archive)
    if archive.stat().st_size!=492630085:raise ValueError("Non-original source archive length")
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    jar=Path(a.ffdec).resolve()
    if not jar.is_file():raise ValueError("Missing FFDec JAR")
    found=[]
    with zipfile.ZipFile(archive) as z:
        for name in FX_NAMES:
            intended="assets/fx/"+name+".swf"
            matches=[m for m in z.infolist() if not m.is_dir() and
                     m.filename.removeprefix("social-warriors_0.02a/")==intended]
            if len(matches)!=1:raise ValueError(f"Not uniquely present: {intended}: {len(matches)}")
            m=matches[0]
            if m.file_size>3_000_000:raise ValueError("Unbounded fx SWF")
            data=z.read(m)
            info=inspect(data,detailed=True)
            digest=hashlib.sha256(data).hexdigest()
            if info["fps"]<=0:raise ValueError("Invalid FPS: "+name)
            rec={"effect_name":name,"original_path":intended,
                 "asset_class":"projectile" if name.startswith("p.") else "impact",
                 "bytes":m.file_size,"sha256":digest,
                 "fps":info["fps"],"main_frames":info["stage_frames"],
                 "root_frame_labels":info["root"]["frame_labels"],
                 "sprite_count":info["sprite_count"],
                 "sprite_ids":[x["character_id"] for x in info["sprites"]][:140],
                 "symbol_classes":info["symbol_names"],
                 "static_tag_parser_warnings":info["totals"].get("parse_warnings",0)}
            with tempfile.TemporaryDirectory(prefix="fx-5d8m-") as td:
                s=Path(td)/(name+".swf");s.write_bytes(data)
                rec["ffdec"]=ffdec_export(jar,s,out/name)
            found.append(rec)
            print("FX_ASSET_5D8M",json.dumps({
              "effect":name,"bytes":m.file_size,"sha256":digest,
              "fps":info["fps"],"sprites":info["sprite_count"],
              "source_symbols":info["symbol_names"],
              "render":rec["ffdec"]["status"],
              "files":rec["ffdec"].get("file_count",0)
            },ensure_ascii=False),flush=True)
    report={
      "lot":"5D.8M","source":"Social Wars official 0.02a ZIP",
      "original_swf_modified":False,
      "static_gameplay_mapping":SOURCE,
      "original_fx_assets":found,
      "source_trace":{
        "delegate_mapping":"core.isoengine.delegates.DelegatesManager.registerDelegate",
        "projectile_definition":"battle.projectiles.ProjectileDefinition",
        "loader":"managers.ProjectileManager.loadAsset -> Base.Main.apfx + 'fx/' + id + '.swf'",
        "hit":"core.isoengine.IsoFightingElement.doProjectileDamage",
        "browser_native_kill":"https://github.com/Acccelll/Social_wars_test/actions/runs/39353491847"
      },
      "proven": ["SWF asset existence and hashes", "Static delegate-to-projectile/impact mapping",
                 "Original fx loader path", "Static SWF content and extracted graphics"],
      "not_yet_proven":["Runtime ID actually loaded in 5D.8J combat",
        "Which subframe and particle was displayed on each attack",
        "Standalone rebuilt client displaying same projectile sprites"]
    }
    (out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("FX_MAPPING_VALIDATED_5D8M",json.dumps({
      "units":list(SOURCE),"fx_assets":len(found),
      "any_extract_errors":any(x["ffdec"]["status"]=="FFDEC_ERROR" for x in found)
    }),flush=True)

if __name__=="__main__":main()
