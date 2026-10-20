#!/usr/bin/env python3
"""5D.8J - bounded read-only extraction of original battle/event-flow AVM2.
All class evidence comes from the original SHA-pinned client; no SWF edits.
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
TARGET=[
 "core.TutorialMain", "core.isoengine.IsoFightingElement",
 "core.isoengine.IsoUnit", "core.isoengine.IsoElement",
 "battle.IAAttack", "battle.Battle", "core.MapInitializer",
 "core.isoengine.IsoMap", "core.isoengine.IsoEngine",
 "core.isoengine.IsoUnitDelegate", "core.isoengine.delegates.AbstractUnitDelegate",
 "core.Scene","core.Base","core.isoengine.IsoInteractiveElement",
 "battle.Assault","battle.IA","popups.PopUpBattleOptions","core.Constants"
]
TERMS=["MOUSE_DOWN","MOUSE_UP","CLICK","mouseDown","mouseUp","attack",
       "IAAttack","startBattle","recibirAtaque","calculateDamage",
       "target","enemy","spawnEnemies","checkStepBattle",
       "STEP_CLICK_ENEMY","STEP_WAIT_BATTLE","IsoFightingElement",
       "PLAYER_ENEMY","PLAYER_SELF","beginBattle","onMouseDown",
       "onMouseUp","addEventListener","onClick","ATTACK"]
METHOD=re.compile(r"\b(?:public|private|protected|internal)?\s*(?:override\s+|static\s+|final\s+)*function\s+([A-Za-z_$][\w$]*)\s*\(",re.M)
CLASS_RE=re.compile(r"^([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s+\d+\s*$",re.M)

def run(jar,args,log,timeout=170):
    try:
        r=subprocess.run(["java","-Xmx3g","-Djava.awt.headless=true","-jar",str(jar),
                          "-cli",*args],capture_output=True,text=True,errors="replace",timeout=timeout)
        log.write_text((r.stdout+"\n"+r.stderr)[-1200000:],encoding="utf-8")
        return dict(code=r.returncode,timeout=False,stdout=r.stdout)
    except subprocess.TimeoutExpired as e:
        s=e.stdout or b""
        if isinstance(s,bytes):s=s.decode("utf-8","replace")
        log.write_text(s[-1200000:],encoding="utf-8")
        return dict(code=None,timeout=True,stdout=s)
def main():
    p=argparse.ArgumentParser()
    for flag in ("archive","ffdec","out"):p.add_argument("--"+flag,required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    jar=Path(a.ffdec).resolve()
    with tempfile.TemporaryDirectory(prefix="sw-original-battle-") as td:
        swf=Path(td)/ORIGINAL
        with zipfile.ZipFile(a.archive) as z:
            files=[f for f in z.infolist() if not f.is_dir() and PurePosixPath(f.filename).name==ORIGINAL]
            if len(files)!=1:raise ValueError("Expected one original SWF")
            with z.open(files[0]) as r, swf.open("wb") as w:shutil.copyfileobj(r,w)
        sha=hashlib.file_digest(swf.open("rb"),"sha256").hexdigest()
        if sha!=SHA:raise ValueError("Unexpected SWF hash: "+sha)
        listing=run(jar,["-dumpAS3",str(swf)],out/"dump_classes.log",190)
        present=set(CLASS_RE.findall(listing["stdout"]))
        selected=[name for name in TARGET if name in present]
        nearby=sorted(name for name in present if
          (re.search(r"(battle|attack|fighting|war|combat|isoengine)",name,re.I)))[:150]
        if len(selected)<3:
            raise RuntimeError("Expected combat classes not found. Check dump_classes.log")
        export={}
        for fmt in ("as","pcode"):
            folder=out/("as3_"+fmt)
            folder.mkdir(exist_ok=True)
            export[fmt]=run(jar,[
              "-selectclass",",".join(selected),"-format","script:"+fmt,
              "-timeout","25","-exportFileTimeout","60",
              "-exportTimeout","175","-export","script",str(folder),str(swf)
            ],out/("export_"+fmt+".log"),205)
        entries=[]
        for fmt in ("as","pcode"):
            for f in sorted((out/("as3_"+fmt)).rglob("*")):
                if not f.is_file() or f.suffix not in (".as",".pcode"):continue
                source=f.read_text(encoding="utf-8",errors="replace")
                if len(source)>2200000:continue
                found=[]
                for term in TERMS:
                    for match in list(re.finditer(re.escape(term),source,re.I))[:35]:
                        # Small windows only, never raw full SWF bytes as metadata.
                        lo=max(0,source.rfind("\n",0,max(0,match.start()-220)))
                        hi=source.find("\n",min(len(source),match.end()+220))
                        if hi<0:hi=min(len(source),match.end()+220)
                        snippet=source[lo:hi].strip().replace("\r","")[:530]
                        found.append({"term":term,"line":source.count("\n",0,match.start())+1,"excerpt":snippet})
                entries.append({
                   "file":f.relative_to(out).as_posix(),
                   "format":fmt,
                   "bytes":len(source),
                   "methods":sorted(set(METHOD.findall(source)))[:260] if fmt=="as" else [],
                   "evidence":found[:180]
                })
        summary={
            "lot":"5D.8J","original_client":ORIGINAL,"sha256":sha,
            "source":"FFDec 26.3.0 on exact original Flash binary",
            "dump_timeout":listing["timeout"],"dump_returncode":listing["code"],
            "requested_classes":TARGET,"verified_present_classes":selected,
            "battle_adjacent_class_names":nearby,
            "export_status":{k:{"returncode":v["code"],"timed_out":v["timeout"]} for k,v in export.items()},
            "exported_files":entries,
            "combat_runtime_verified":False,
            "warning":"Static class/callsite analysis does not prove an event executed. An original UI combat test is still required."
        }
        (out/"battle_state_index.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
        print("ORIGINAL_BATTLE_5D8J",json.dumps({
           "selected_classes":selected,
           "exported":{k:sum(x["format"]==k for x in entries) for k in ("as","pcode")},
           "interesting_methods":{x["file"]:x["methods"][:100] for x in entries if x["format"]=="as"},
           "evidence_counts":{x["file"]:len(x["evidence"]) for x in entries}
        },ensure_ascii=False),flush=True)
if __name__=="__main__":main()
