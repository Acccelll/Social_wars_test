#!/usr/bin/env python3
"""5D.8M: read-only original AVM2 projectile/effect call-site and asset inventory.

Deliberately separates exact source-derived symbol names from hypotheses.
Full decompilation stays in short-lived Actions artifact; repository metadata
contains bounded, attributed excerpts only. Never edit original SWF or saves.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ORIGINAL="Basesec_1.5.4.swf"
SHA="e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"
NEEDED=[
 "battle.projectiles.ProjectileDefinition",
 "managers.ProjectileManager",
 "battle.projectiles.AbstractProjectile",
 "battle.projectiles.models.Blast",
 "battle.projectiles.models.Trail",
 "battle.projectiles.models.ParabolicProjectile",
 "battle.projectiles.models.Beam",
 "battle.projectiles.Machinegun",
 "battle.projectiles.models.Grenade",
 "battle.projectiles.models.MovieProjectile",
 "battle.projectiles.models.BeamBlast",
 "core.isoengine.delegates.units.ProjectileDelegate",
 "core.isoengine.delegates.units.DoubleProjectileDelegate",
 "core.isoengine.IsoFightingElement",
 "core.isoengine.IsoUnit",
 "core.ManagerParticles",
 "core.Particle",
 "core.SFXType"
]
WATCH=[
 "ProjectileDefinition","PROJECTILE_","BLAST_","TRAIL_",
 "ProjectileManager","addProjectile","shootProjectile",
 "doProjectileDamage","blastID","blastRadius","projectileID",
 "projectileType","ProjectileMC","BlastMC","ShotgunBlastMC",
 "getProjectileSound","getProjectilePoint","landed",
 "addParticle","onAttack","playGunAnimation","updateAttack"
]
METHOD=re.compile(r"\b(?:public|private|protected|internal)?\s*(?:override\s+|static\s+|final\s+)*function\s+([A-Za-z_$][\w$]*)\s*\(",re.M)
CLASS=re.compile(r"^([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s+\d+\s*$",re.M)
ASSET_HINT=re.compile(r"(projectil|bullet|impact|blast|explos|laser|beam|shot|muzzle|particle|weapon|fx|fire)",re.I)

def ffdec(jar,argv,output,timeout=180):
    try:
        p=subprocess.run(["java","-Xmx3g","-Djava.awt.headless=true","-jar",str(jar),
                         "-cli",*argv],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         text=True,errors="replace",timeout=timeout)
        output.write_text(p.stdout[-300000:],encoding="utf-8")
        return {"code":p.returncode,"timeout":False,"stdout":p.stdout}
    except subprocess.TimeoutExpired as e:
        body=e.stdout or b""
        if isinstance(body,bytes):body=body.decode("utf-8","replace")
        output.write_text(body[-300000:],encoding="utf-8")
        return {"code":None,"timeout":True,"stdout":body}

def scan_methods(src):
    # Capture a function body with brace depth; AS3 decompiler output may
    # include braces in strings, so only use as a bounded textual index.
    result=[]
    for m in METHOD.finditer(src):
        name=m.group(1)
        opening=src.find("{",m.end())
        if opening<0 or opening-m.end()>350:continue
        depth=0
        end=len(src)
        for i in range(opening,len(src)):
            if src[i]=="{":depth+=1
            elif src[i]=="}":
                depth-=1
                if depth==0:
                    end=i+1
                    break
        body=src[m.start():end]
        terms=[t for t in WATCH if t.lower() in body.lower()]
        if not terms and not re.search(r"projectil|attack|blast|fire|shoot|particle",name,re.I):continue
        lines=body.splitlines()
        hitlines=[(i+1,ln.strip()) for i,ln in enumerate(lines)
                  if any(t.lower() in ln.lower() for t in WATCH)]
        result.append({
          "method":name,
          "method_source_line":src.count("\n",0,m.start())+1,
          "source_length":len(body),
          "terms":terms[:35],
          "relevant_lines":[{"offset":i,"text":s[:450]} for i,s in hitlines[:20]],
          "decompiler_confidence":"method-level static source only"
        })
    return result

def main():
    ap=argparse.ArgumentParser()
    for k in ("archive","ffdec","out"):ap.add_argument("--"+k,required=True)
    a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    jar=Path(a.ffdec).resolve()
    if not jar.is_file():raise ValueError("Missing FFDec JAR")
    if Path(a.archive).stat().st_size!=492630085:raise ValueError("Unexpected archive size")
    with zipfile.ZipFile(a.archive) as archive, tempfile.TemporaryDirectory(prefix="sw-original-5d8m-") as td:
        members=[m for m in archive.infolist() if not m.is_dir()]
        originals=[m for m in members if PurePosixPath(m.filename).name==ORIGINAL]
        if len(originals)!=1:raise ValueError("Ambiguous original main SWF")
        original=Path(td)/ORIGINAL
        with archive.open(originals[0]) as reader,original.open("wb") as writer:
            shutil.copyfileobj(reader,writer)
        sha=hashlib.file_digest(original.open("rb"),"sha256").hexdigest()
        if sha!=SHA:raise ValueError("Unexpected original SWF SHA")
        names=ffdec(jar,["-dumpAS3",str(original)],out/"dump_as3.log",175)
        present=set(CLASS.findall(names["stdout"]))
        selected=[n for n in NEEDED if n in present]
        missing=[n for n in NEEDED if n not in present]
        if "battle.projectiles.ProjectileDefinition" not in selected or "managers.ProjectileManager" not in selected:
            raise ValueError("Essential original projectile classes unavailable")
        if len(selected)<12:raise ValueError("Projectile class set too small")
        exports={}
        for fmt in ("as","pcode"):
            dest=out/("as3_"+fmt)
            dest.mkdir(exist_ok=True)
            exports[fmt]=ffdec(jar,[
              "-selectclass",",".join(selected),
              "-format","script:"+fmt,
              "-timeout","25","-exportFileTimeout","55",
              "-exportTimeout","180","-export","script",str(dest),str(original)
            ],out/("export_"+fmt+".log"),215)
        summaries=[]
        for f in sorted((out/"as3_as").rglob("*.as")):
            src=f.read_text(encoding="utf-8",errors="replace")
            if len(src)>2000000:continue
            data=scan_methods(src)
            summaries.append({
              "source_file":f.relative_to(out).as_posix(),
              "method_count":len(METHOD.findall(src)),
              "related_methods":data[:100],
              "source_size":len(src)
            })
        effects=[]
        for m in members:
            base=PurePosixPath(m.filename).name
            if not m.filename.lower().endswith(".swf"):continue
            if not ASSET_HINT.search(base):continue
            effects.append({
              "source_path":m.filename.removeprefix("social-warriors_0.02a/"),
              "size_bytes":m.file_size,
              "filename_match_only":True
            })
        summary={
         "lot":"5D.8M",
         "source_original":ORIGINAL,"sha256":sha,
         "original_swf_untouched":True,
         "requested_classes":NEEDED,"found_classes":selected,
         "missing_classes":missing,
         "class_listing_status":{"code":names["code"],"timeout":names["timeout"]},
         "exports":{k:{"code":v["code"],"timeout":v["timeout"]} for k,v in exports.items()},
         "method_summaries":summaries,
         "related_external_swf_filenames":effects[:140],
         "external_swf_filename_matches_total":len(effects),
         "limitations":["Filename matches alone do not prove an effect was loaded.",
           "A ProjectileDefinition constant by itself does not identify a rendered DefineSprite.",
           "Without client instrumentation, recording-to-frame mapping remains unresolved."]
        }
        (out/"projectile_call_graph.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("ORIGINAL_PROJECTILES_5D8M",json.dumps({
          "found_classes":selected,
          "missing_classes":missing,
          "extracted_as3_classes":len(summaries),
          "relevant_methods":sum(len(x["related_methods"]) for x in summaries),
          "candidate_asset_filenames":len(effects),
          "method_samples":{x["source_file"]: [m["method"] for m in x["related_methods"][:20]]
                            for x in summaries}
        },ensure_ascii=False),flush=True)
if __name__=="__main__":main()
