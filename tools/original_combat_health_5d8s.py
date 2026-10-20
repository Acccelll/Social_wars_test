#!/usr/bin/env python3
"""5D.8S: recover authentic AS3 damage, health-bar and death lifecycle.

This tool only reads the SHA-pinned original 0.02a SWF and exports a
bounded subset of AS3+Pcode; it never patches/rewrites the original.
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

SWF_NAME="Basesec_1.5.4.swf"
SWF_SHA="e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77"
CLASSES=[
 "battle.HealthBar",
 "battle.projectiles.AbstractProjectile",
 "core.isoengine.IsoFightingElement",
 "core.isoengine.IsoUnit",
 "core.Particle",
 "core.Config",
 "core.isoengine.delegates.units.ProjectileDelegate"
]
SEARCH={
 "battle.HealthBar":["set","setMaxValue","setScale"],
 "core.isoengine.IsoFightingElement":[
  "calculateDamage","recibirAtaque","_showDamageParticle",
  "updateVida","shootProjectile","doProjectileDamage","die"],
 "core.isoengine.IsoUnit":["die","playGunAnimation","IA_Attack"],
 "battle.projectiles.AbstractProjectile":[],
 "core.Particle":[],
 "core.Config":[],
 "core.isoengine.delegates.units.ProjectileDelegate":["onDelayedAttack"]
}
PAT=re.compile(r"\b(?:public|private|protected|internal)\s+(?:override\s+)?function\s+([A-Za-z_]\w*)\s*\(")
HINTS=("iHealth","maxLife","barraVida","_damageToDisplay","health","killedSignal",
       "damageDone","nearDeath","showDamageParticle","kill","recibirAtaque",
       "setMaxValue","landed","addOnce","projectile")

def main():
 p=argparse.ArgumentParser()
 for a in ("archive","ffdec","out"):p.add_argument("--"+a,required=True)
 a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
 if Path(a.archive).stat().st_size!=492630085:raise ValueError("Unexpected original archive length")
 with tempfile.TemporaryDirectory(prefix="original-health-5d8s-") as td,zipfile.ZipFile(a.archive) as z:
  matches=[m for m in z.infolist() if not m.is_dir() and PurePosixPath(m.filename).name==SWF_NAME]
  if len(matches)!=1:raise ValueError("Original client is missing/ambiguous")
  swf=Path(td)/SWF_NAME
  with z.open(matches[0]) as stream,swf.open("wb") as writer:shutil.copyfileobj(stream,writer)
  sha=hashlib.sha256(swf.read_bytes()).hexdigest()
  if sha!=SWF_SHA:raise ValueError("Original game SWF SHA mismatch")
  for fmt in ("as","pcode"):
   dest=out/("as3_"+fmt);dest.mkdir(parents=True,exist_ok=True)
   argv=["java","-Xmx3g","-Djava.awt.headless=true","-jar",str(Path(a.ffdec).resolve()),"-cli",
     "-selectclass",",".join(CLASSES),"-format","script:"+fmt,
     "-timeout","25","-exportFileTimeout","60","-exportTimeout","160",
     "-export","script",str(dest),str(swf)]
   proc=subprocess.run(argv,capture_output=True,text=True,errors="replace",timeout=185)
   (out/("ffdec_"+fmt+".log")).write_text((proc.stdout+"\n"+proc.stderr)[-12000:])
   if proc.returncode:raise ValueError("FFDec "+fmt+" returned "+str(proc.returncode))
 summary={"lot":"5D.8S","source_swf_sha256":sha,"original_swf_modified":False,
 "classes_requested":CLASSES,"classes_present":[],"methods":{},"static_claims":[],
 "limitations":[
  "The original game internally tracks mutable iHealth; saves are not reliable per-hit telemetry.",
  "Damage number visuals may be aggregated or throttled before display.",
  "Code inspection cannot prove specific values, exact timings or client state in a captured video."
 ]}
 for file in sorted((out/"as3_as").rglob("*.as")):
  class_name=file.relative_to(out/"as3_as").as_posix().removeprefix("scripts/").removesuffix(".as").replace("/",".")
  text=file.read_text(encoding="utf-8",errors="replace")
  summary["classes_present"].append(class_name)
  methods=[]
  for m in PAT.finditer(text):
   method=m.group(1)
   if method not in SEARCH.get(class_name,[]) and class_name not in [
      "battle.HealthBar","battle.projectiles.AbstractProjectile"]:continue
   left=m.start();line=text.count("\n",0,left)+1
   window=text[left:min(len(text),left+5000)]
   methods.append({"name":method,"line":line,"source_start":window[:300].replace("\n"," "),
      "relevant_statements":[
       {"line":line+i,"source":row.strip()[:330]}
       for i,row in enumerate(window.splitlines()[:135]) if any(w.lower() in row.lower() for w in HINTS)
      ][:25]
   })
  summary["methods"][class_name]=methods
 needed=["battle.HealthBar","core.isoengine.IsoFightingElement","core.isoengine.IsoUnit"]
 if not all(k in summary["classes_present"] for k in needed):raise ValueError("Healthbar/life engine classes not found")
 names={m["name"] for m in summary["methods"]["core.isoengine.IsoFightingElement"]}
 if not {"recibirAtaque","updateVida","die","calculateDamage","doProjectileDamage"}<=names:
  raise ValueError("Missing lifecycle methods in original client")
 (out/"life_cycle_index.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
 print("LIFECYCLE_SOURCE_5D8S",json.dumps({
 "sha256":sha,"classes":summary["classes_present"],
 "lifecycle_methods":sorted(names),
 "health_bar_methods":[x["name"] for x in summary["methods"]["battle.HealthBar"]]
 },ensure_ascii=False),flush=True)
if __name__=="__main__":main()
